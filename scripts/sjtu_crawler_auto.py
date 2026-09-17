#!/usr/bin/env python3
"""
上海交大体育预约系统 - 场地数据爬虫
爬取笼式足球场预约数据, 写入Supabase数据库

登录策略:
  1. 优先加载已保存的登录态 (output/auth_state.json)
  2. 登录态过期 → OCR验证码自动登录 → 保存新登录态
  3. OCR失败 → 提示手动运行 save_auth.py
"""

import asyncio
import base64
import io
import json
import os
import re
import sys
import requests
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# OCR
try:
    from PIL import Image
    import pytesseract
    t_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(t_path):
        pytesseract.pytesseract.tesseract_cmd = t_path
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
except ImportError:
    pass

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
AUTH_FILE = Path(__file__).parent.parent / 'output' / 'auth_state.json'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

VENUES = [{
    'name': '笼式足球场',
    'venue_id': '2b528fa8-3ce8-4a7a-8f8b-83cc537901ed',
    'field_type': 'ad666603-a47e-488d-b913-d5304a880ced',
}]

ACCOUNT = {
    'username': os.getenv('SJTU_USERNAME', ''),
    'password': os.getenv('SJTU_PASSWORD', '')
}

BASE_URL = 'https://sports.sjtu.edu.cn'


# ─── Supabase ───────────────────────────────────────

def save_to_supabase(slots):
    if not slots:
        print("没有数据")
        return True
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    try:
        print("清理旧数据...")
        for v in VENUES:
            r = requests.delete(
                f'{SUPABASE_URL}/rest/v1/time_slots?venue_id=eq.{v["venue_id"]}',
                headers=headers, timeout=30)
            if r.status_code not in [200, 204]:
                print(f"  ERR {v['name']}: {r.status_code} {r.text[:100]}")
                return False
            print(f"  OK {v['name']}")

        print(f"写入 {len(slots)} 条...")
        records = [{
            'venue_id': s['venue_id'], 'date': s['date'],
            'field_name': s['field_name'], 'time': s['time'],
            'price': s['price'], 'remaining': s['remaining'],
            'status': s['status']
        } for s in slots]

        url = f'{SUPABASE_URL}/rest/v1/time_slots'
        for i in range(0, len(records), 1000):
            batch = records[i:i+1000]
            r = requests.post(url, headers=headers, json=batch, timeout=30)
            if r.status_code not in [200, 201]:
                print(f"  ERR: {r.status_code} {r.text[:100]}")
                return False
            print(f"  OK {len(batch)}条")
        return True
    except Exception as e:
        print(f"ERR: {e}")
        return False


# ─── API 调用 ───────────────────────────────────────

async def call_api(page, url, data, desc=""):
    """在浏览器内发fetch, 自动带完整cookie"""
    r = await page.evaluate("""
    async ([u,d]) => {
        try {
            const r = await fetch(u,{method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify(d),credentials:'include'});
            return {s:r.status, ok:r.ok, t:await r.text()};
        } catch(e) { return {s:0, ok:false, t:'', err:e.message}; }
    }
    """, [url, data])
    if r.get('err'): print(f"  ERR {desc}: {r['err']}"); return None
    if not r['ok'] or not r['t']: print(f"  ERR {desc}: HTTP {r['s']}"); return None
    if '<title>登录</title>' in r['t']:
        print(f"  ERR {desc}: 未登录")
        return None
    try: return json.loads(r['t'])
    except: print(f"  ERR {desc}: 非JSON"); return None


# ─── 数据解析 ───────────────────────────────────────

STATUS_MAP = {'-3':'已满','-2':'未开放','-1':'不可选','0':'可预约','1':'已预约'}

def format_slots(venue_id, fields, date):
    result = []
    for fd in fields:
        for i, s in enumerate(fd.get('priceList', [])):
            h = 7 + i
            if 14 <= h <= 21:
                result.append({
                    'venue_id': venue_id, 'date': date,
                    'field_name': fd.get('fieldName'),
                    'time': f'{h:02d}:00',
                    'price': s.get('price', '0'),
                    'remaining': s.get('count', 0),
                    'status': STATUS_MAP.get(str(s.get('status','-1')), '未知')
                })
    return result


# ─── OCR 验证码识别 ─────────────────────────────────

def ocr_captcha_multi(img_data, retry_num=0):
    """识别jAccount验证码, 返回多个候选(按可信度排序)"""
    if not HAS_OCR:
        return []
    img = Image.open(io.BytesIO(img_data))
    w, h = img.size

    bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
    img_rgb = Image.alpha_composite(bg, img).convert('RGB')

    dbg_dir = Path(__file__).parent.parent / 'output'
    dbg_dir.mkdir(exist_ok=True)
    img_rgb.save(dbg_dir / f'captcha_rgb_{retry_num}.png')

    result_counts = {}  # {text: count}
    whitelist = 'abcdefghijklmnopqrstuvwxyz'

    r, g, b = img_rgb.split()
    gray = img_rgb.convert('L')

    for label, channel in [('gray', gray), ('R', r), ('G', g), ('B', b)]:
        big = channel.resize((w * 5, h * 5), Image.LANCZOS)
        for th in [80, 90, 100, 110, 120, 130, 140]:
            bw = big.point(lambda x, t=th: 0 if x < t else 255)

            for cfg in [f'--psm 8 -c tessedit_char_whitelist={whitelist}',
                        f'--psm 7 -c tessedit_char_whitelist={whitelist}']:
                t = pytesseract.image_to_string(bw, config=cfg).strip()
                t = re.sub(r'[^a-z]', '', t)
                if 4 <= len(t) <= 6:
                    result_counts[t] = result_counts.get(t, 0) + 1

    # 按投票数排序, 相同投票数优先5字符
    sorted_results = sorted(result_counts.items(),
                           key=lambda x: (-x[1], abs(len(x[0])-5)))
    return [t for t, _ in sorted_results]


# ─── jAccount 登录 ──────────────────────────────────

async def jaccount_login(page):
    """通过jAccount密码+OCR验证码登录, 返回是否成功

    结果判定: 拦截/jaccount/ulogin的JSON响应 (页面文案不可靠)
      WRONG_CAPTCHA → 验证码错; 服务端会自动换图, 重新OCR再试
      WRONG_USER_OR_PASSWORD → 账号密码错, 立即失败
    每轮只提交OCR Top1候选: 提交失败后验证码已被服务端换掉, 旧候选无意义
    """
    if not HAS_OCR:
        print("  [ERR] OCR不可用(pytesseract/tesseract未安装)")
        return False

    print("  正在OCR识别验证码...")
    ulogin = {'json': None}
    seen_resp = []

    async def on_response(resp):
        url = resp.url
        if 'jaccount' not in url:
            return
        if any(x in url for x in ['.css', '.js', '.ico', '.woff', '.svg']):
            return
        seen_resp.append(f'{resp.status} {url[:110]}')
        if '/jaccount/ulogin' not in url:
            return
        try:
            body = await resp.text()
            seen_resp.append(f'    ulogin body: {body[:200]}')
            ulogin['json'] = json.loads(body)
        except Exception as e:
            seen_resp.append(f'    ulogin body读取失败: {e}')
            ulogin['json'] = None

    page.on('response', on_response)

    try:
        for retry in range(8):
            # 获取验证码图片
            b64 = await page.evaluate("""
            async () => {
                let img = document.getElementById('captcha-img');
                if (!img) {
                    for (const i of document.querySelectorAll('img'))
                        if (i.src && i.src.includes('captcha?') && i.naturalWidth > 0)
                            { img = i; break; }
                }
                if (!img) return null;
                const c = document.createElement('canvas');
                c.width = img.naturalWidth; c.height = img.naturalHeight;
                c.getContext('2d').drawImage(img, 0, 0);
                return c.toDataURL('image/png').split(',')[1];
            }
            """)
            if not b64:
                print("  [ERR] 无法获取验证码")
                break

            img_data = base64.b64decode(b64)
            candidates = ocr_captcha_multi(img_data, retry)
            print(f"  OCR #{retry+1} candidates: {candidates}")

            if not candidates:
                await page.evaluate("typeof refreshCaptcha==='function'&&refreshCaptcha()")
                await asyncio.sleep(1)
                continue

            captcha = candidates[0]
            ulogin['json'] = None
            captcha_input = page.locator('#input-login-captcha')
            await captcha_input.fill(captcha)
            await captcha_input.blur()
            await asyncio.sleep(0.5)
            await page.locator('#submit-password-button').click()

            # 等服务端响应或跳转完成
            for _ in range(36):
                if 'jaccount' not in page.url or ulogin['json'] is not None:
                    break
                await asyncio.sleep(0.5)

            if 'jaccount' not in page.url:
                print(f"  OK jAccount登录成功! captcha='{captcha}'")
                return True

            code = ulogin['json'].get('code') if ulogin['json'] else None
            if code == 'WRONG_USER_OR_PASSWORD':
                print("  [ERR] 用户名或密码错误!")
                return False
            if code == 'WRONG_CAPTCHA':
                print(f"  验证码错误 (提交'{captcha}'), 换图重试")
                continue

            # 无响应或非标准响应: 再等跳转, 然后留下诊断现场
            for _ in range(20):
                if 'jaccount' not in page.url:
                    break
                await asyncio.sleep(0.5)
            if 'jaccount' not in page.url:
                print(f"  OK jAccount登录成功! captcha='{captcha}'")
                return True

            diag_dir = OUTPUT_DIR / 'diag'
            diag_dir.mkdir(parents=True, exist_ok=True)
            try:
                await page.screenshot(path=str(diag_dir / f'login_retry{retry}.png'))
            except Exception as e:
                print(f"  [诊断] 截图失败: {e}")
            try:
                text = (await page.locator('body').inner_text())[:300]
            except Exception:
                text = '<读取失败>'
            if '二次验证' in text:
                print("  [ERR] 账号密码与图形验证码均已通过, 但jAccount要求二次验证(短信/邮箱/交我办)")
                print("  [ERR] 这是海外IP/陌生浏览器环境触发的风控, 无法自动完成")
                print("  [ERR] 解决: 在国内IP环境(本机)运行 save_auth.py 或直接运行爬虫完成一次登录,")
                print("  [ERR] 并勾选'信任此浏览器'; 之后可用AUTH_STATE登录态供CI使用, 或改用本机定时运行")
                return False
            print(f"  [诊断] retry={retry} 提交'{captcha}'后无跳转")
            print(f"  [诊断] URL: {page.url[:130]}")
            print(f"  [诊断] 页面文本: {text!r}")
            print(f"  [诊断] jaccount响应链(最近10条):")
            for line in seen_resp[-10:]:
                print(f"    {line}")
            # 可能是慢响应/瞬时风控: 换图进入下一轮
            await page.evaluate("typeof refreshCaptcha==='function'&&refreshCaptcha()")
            await asyncio.sleep(1)
    finally:
        page.remove_listener('response', on_response)

    return False


# ─── 保存登录态 ─────────────────────────────────────

async def save_auth(context, page):
    cookies = await context.cookies()
    auth_data = {
        'cookies': cookies,
        'url': page.url,
        'saved_at': datetime.now().isoformat()
    }
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(AUTH_FILE, 'w', encoding='utf-8') as f:
        json.dump(auth_data, f, ensure_ascii=False, indent=2)
    print(f"  登录态已保存 ({len(cookies)} cookies)")


# ─── 主流程 ────────────────────────────────────────

def validate_config():
    missing = [n for n, v in [
        ('SUPABASE_URL', SUPABASE_URL), ('SUPABASE_KEY', SUPABASE_KEY),
        ('SJTU_USERNAME', ACCOUNT['username']), ('SJTU_PASSWORD', ACCOUNT['password'])
    ] if not v]
    if missing:
        print(f"ERR 缺少环境变量: {missing}")
        return False
    return True


async def main():
    print("=" * 50)
    print(f"上海交大体育预约 - {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 50)
    if not validate_config():
        return

    # 加载旧登录态
    saved_auth = None
    if AUTH_FILE.exists():
        try:
            with open(AUTH_FILE, 'r', encoding='utf-8') as f:
                saved_auth = json.load(f)
            print(f"加载登录态: {len(saved_auth.get('cookies', []))} cookies")
        except (json.JSONDecodeError, OSError) as e:
            print(f"登录态文件损坏, 忽略并重新登录: {e}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
            locale='zh-CN',
        )
        if saved_auth and saved_auth.get('cookies'):
            await context.add_cookies(saved_auth['cookies'])

        page = await context.new_page()

        try:
            # ─── 验证登录态 ───
            print("\n验证登录态...")
            await page.goto(f'{BASE_URL}/pc/', timeout=30000)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            # 快速检测: 调API看是否返回登录页
            test = await call_api(page,
                f'{BASE_URL}/manage/fieldDetail/queryFieldReserveSituationIsFull',
                {'id': VENUES[0]['venue_id'],
                 'feildType': VENUES[0]['field_type'], 'date': ''},
                "检测登录态")

            need_login = (test is None)

            if need_login:
                print("登录态已过期, 尝试自动登录...")
                # 已失效的cookies会干扰oauth2/authorize的跳转流程(页面到不了jAccount),
                # 登录前必须清空
                await context.clear_cookies()
                # ─── jAccount自动登录 ───
                await page.goto(f'{BASE_URL}/pc/', timeout=30000)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                # 点击校内人员登录 (最多3次尝试)
                for attempt in range(3):
                    await page.get_by_role("button", name="校内人员登录").click()
                    await asyncio.sleep(5)
                    await page.wait_for_load_state('networkidle')
                    if 'jaccount' in page.url:
                        break
                    print(f"  未跳转到jAccount (第{attempt+1}次), 重试...")
                    await page.goto(f'{BASE_URL}/pc/', timeout=30000)
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(2)

                if 'jaccount' in page.url:
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(2)
                    await page.fill('#input-login-user', ACCOUNT['username'])
                    await page.fill('#input-login-pass', ACCOUNT['password'])

                    ok = await jaccount_login(page)
                    if not ok:
                        print("\n自动登录失败! 请手动运行: python scripts/save_auth.py")
                        await browser.close()
                        return

                    # 登录成功 → 保存登录态
                    await save_auth(context, page)
                    # 回到体育网站
                    await page.goto(f'{BASE_URL}/pc/', timeout=30000)
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(2)
                else:
                    diag_dir = OUTPUT_DIR / 'diag'
                    diag_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        await page.screenshot(path=str(diag_dir / 'no_redirect.png'))
                    except Exception:
                        pass
                    try:
                        text = (await page.locator('body').inner_text())[:300]
                    except Exception:
                        text = '<读取失败>'
                    print("  [诊断] 点击登录后未跳转, 现场:")
                    print(f"  [诊断] URL: {page.url[:130]}")
                    print(f"  [诊断] 页面文本: {text!r}")
                    print("  未跳转到jAccount, 登录流程异常")
                    await browser.close()
                    return
            else:
                print("OK 登录态有效")

            # ─── 爬取数据 ───
            all_slots = []
            for venue in VENUES:
                print(f"\n--- {venue['name']} ---")
                result = await call_api(page,
                    f'{BASE_URL}/manage/fieldDetail/queryFieldReserveSituationIsFull',
                    {'id': venue['venue_id'], 'feildType': venue['field_type'], 'date': ''},
                    "查询日期")
                if not result or result.get('code') != 0:
                    print(f"  失败: {result and result.get('msg')}")
                    continue

                dates = result.get('data', [])
                if not dates:
                    print("  无可用日期")
                    continue
                print(f"  {len(dates)} 个日期")

                for i, d in enumerate(dates):
                    if i > 0:
                        await asyncio.sleep(0.5)
                    date, did = d['date'], d['dateId']
                    r = await call_api(page,
                        f'{BASE_URL}/manage/fieldDetail/queryFieldSituation',
                        {'fieldType': venue['field_type'], 'date': date,
                         'venueId': venue['venue_id'], 'dateId': did}, date)
                    if r and r.get('code') == 0 and r.get('data'):
                        slots = format_slots(venue['venue_id'], r['data'], date)
                        all_slots.extend(slots)
                        n = sum(1 for s in slots if s['status'] == '可预约')
                        print(f"    {date}: {n}可预约 共{len(slots)}条")
                    else:
                        print(f"    {date}: 失败")

        finally:
            await browser.close()

    # ─── 保存 ───
    print(f"\n{'='*50}")
    print(f"总计: {len(all_slots)} 条")
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_DIR / 'all_venues_booking_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'query_time': datetime.now().isoformat(),
            'total_slots': len(all_slots),
            'slots': all_slots
        }, f, ensure_ascii=False, indent=2)
    print(f"JSON: {OUTPUT_DIR / 'all_venues_booking_data.json'}")
    save_to_supabase(all_slots)
    print("=" * 50)


if __name__ == '__main__':
    asyncio.run(main())
