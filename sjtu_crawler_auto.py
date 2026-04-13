#!/usr/bin/env python3
"""
上海交大体育预约系统 - 多场地版本
爬取笼式足球场和致远游泳馆东侧足球场
自动写入Supabase数据库
使用REST API直接调用，无需额外安装库
"""

import asyncio
import json
import os
import requests
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# Supabase配置 - 从环境变量读取
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# 场地配置
VENUES = [
    {
        'name': '笼式足球场',
        'venue_id': '2b528fa8-3ce8-4a7a-8f8b-83cc537901ed',
        'field_type': 'ad666603-a47e-488d-b913-d5304a880ced',
        'sport_type': '足球'
    }
]

# 账号配置 - 从环境变量读取
ACCOUNT = {
    'username': os.getenv('SJTU_USERNAME', ''),
    'password': os.getenv('SJTU_PASSWORD', '')
}

BASE_URL = 'https://sports.sjtu.edu.cn'


def save_to_supabase(time_slots_data):
    """使用REST API保存时段数据到Supabase"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }

        # 【关键修复】删除所有旧数据（不仅仅是当天之前的）
        # 这样可以防止数据重复累积
        print("正在清理旧数据...")
        for venue in VENUES:
            delete_url = f'{SUPABASE_URL}/rest/v1/time_slots?venue_id=eq.{venue["venue_id"]}'
            delete_response = requests.delete(delete_url, headers=headers)
            if delete_response.status_code in [200, 204]:
                print(f"   ✅ 已清理 {venue['name']} 的旧数据")
            else:
                print(f"   ⚠️  清理旧数据: {delete_response.status_code} - {delete_response.text}")

        # 批量插入新数据 (每次最多1000条)
        if time_slots_data:
            print(f"正在写入 {len(time_slots_data)} 条新数据...")
            # Supabase POST /rest/v1/time_slots
            insert_url = f'{SUPABASE_URL}/rest/v1/time_slots'

            # 将数据转换为Supabase格式
            records = []
            for slot in time_slots_data:
                record = {
                    'venue_id': slot['venue_id'],
                    'date': slot['date'],
                    'field_name': slot['field_name'],
                    'time': slot['time'],
                    'price': slot['price'],
                    'remaining': slot['remaining'],
                    'status': slot['status']
                }
                records.append(record)

            # 分批插入（每次1000条）
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                response = requests.post(insert_url, headers=headers, json=batch)

                if response.status_code in [200, 201]:
                    print(f"   ✅ 写入第 {i//batch_size + 1} 批 {len(batch)} 条数据")
                else:
                    print(f"   ❌ 写入失败: {response.status_code} - {response.text}")
                    return False

            print(f"✅ 成功写入 {len(records)} 条数据到Supabase")
            return True
        else:
            print("没有数据需要写入")
            return True

    except Exception as e:
        print(f"❌ Supabase写入失败: {e}")
        return False


async def login_and_get_session():
    """使用Playwright登录并获取session cookie"""
    print("=" * 60)
    print("步骤1: Playwright登录获取Session")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # 无头模式
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. 访问首页
            print("\n[1] 访问首页...")
            await page.goto(f'{BASE_URL}/pc/', timeout=30000)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            # 2. 点击校外人员登录
            print("[2] 点击校外人员登录...")
            await page.get_by_role("button", name="校外人员登录").click()
            await asyncio.sleep(3)

            # 3. 填写账号密码
            print("[3] 填写账号...")
            await page.wait_for_selector('input[placeholder*="账号"]', timeout=10000)
            await page.fill('input[placeholder*="账号"]', ACCOUNT['username'])
            await page.fill('input[placeholder*="密码"]', ACCOUNT['password'])

            # 4. 点击登录
            print("[4] 登录...")
            await page.get_by_role("button", name="登录", exact=True).click()

            # 等待登录完成
            await asyncio.sleep(15)
            await page.wait_for_load_state('networkidle')
            print(f"登录后URL: {page.url}")

            # 获取cookies
            cookies = await context.cookies()
            session_cookie = None
            for cookie in cookies:
                if cookie['name'] == 'JSESSIONID':
                    session_cookie = cookie['value']
                    break

            if session_cookie:
                print(f"✅ 获取到JSESSIONID: {session_cookie[:20]}...")
                return session_cookie
            else:
                print("❌ 未找到JSESSIONID")
                return None

        except Exception as e:
            print(f"登录错误: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()


def query_available_dates(session_id, venue_id, field_type):
    """查询可预约日期"""
    url = f'{BASE_URL}/manage/fieldDetail/queryFieldReserveSituationIsFull'

    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'JSESSIONID={session_id}',
        'Referer': f'{BASE_URL}/pc/'
    }

    data = {
        'id': venue_id,
        'feildType': field_type,
        'date': ''
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        result = response.json()

        if result.get('code') == 0:
            return result.get('data', [])
        else:
            print(f"   ❌ 查询失败: {result.get('msg')}")
            return []

    except Exception as e:
        print(f"   ❌ 请求错误: {e}")
        return []


def query_time_slots(session_id, venue_id, field_type, date, date_id):
    """查询特定日期的时段预约情况"""
    url = f'{BASE_URL}/manage/fieldDetail/queryFieldSituation'

    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'JSESSIONID={session_id}',
        'Referer': f'{BASE_URL}/pc/'
    }

    data = {
        'fieldType': field_type,
        'date': date,
        'venueId': venue_id,
        'dateId': date_id
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        result = response.json()

        if result.get('code') == 0:
            return result.get('data', [])
        else:
            print(f"   ❌ 查询失败: {result.get('msg')}")
            return []

    except Exception as e:
        print(f"   ❌ 请求错误: {e}")
        return []


def parse_slot_status(status_code):
    """解析时段状态码"""
    status_map = {
        '-3': '已满',
        '-2': '未开放',
        '-1': '不可选',
        '0': '可预约',
        '1': '已预约'
    }
    return status_map.get(str(status_code), f'未知({status_code})')


def format_time_slots_data(venue_id, fields_data, date):
    """格式化场地数据为Supabase格式"""
    result = []

    for field in fields_data:
        field_id = field.get('fieldId')
        field_name = field.get('fieldName')

        price_list = field.get('priceList', [])
        for i, slot in enumerate(price_list):
            time_hour = 7 + i  # 从07:00开始

            # 只保留14:00-21:00的时段（与前端一致）
            if time_hour < 14 or time_hour > 21:
                continue

            slot_info = {
                'venue_id': venue_id,
                'date': date,
                'field_name': field_name,
                'time': f'{time_hour:02d}:00',
                'price': slot.get('price', '0'),
                'remaining': slot.get('count', 0),
                'status': parse_slot_status(slot.get('status', '-1'))
            }
            result.append(slot_info)

    return result


def validate_config():
    """验证必需的配置是否已设置"""
    required_vars = [
        ('SUPABASE_URL', SUPABASE_URL),
        ('SUPABASE_KEY', SUPABASE_KEY),
        ('SJTU_USERNAME', ACCOUNT['username']),
        ('SJTU_PASSWORD', ACCOUNT['password'])
    ]
    
    missing_vars = [name for name, value in required_vars if not value]
    
    if missing_vars:
        print("❌ 错误：缺少必需的环境变量！")
        print("\n请创建 .env 文件并设置以下变量：")
        print("  SUPABASE_URL=your-supabase-url")
        print("  SUPABASE_KEY=your-supabase-key")
        print("  SJTU_USERNAME=your-username")
        print("  SJTU_PASSWORD=your-password")
        print("\n或者参考 .env.example 文件进行配置。")
        return False
    
    # 验证 URL 格式
    if not SUPABASE_URL.startswith('http'):
        print(f"❌ 错误：SUPABASE_URL 格式无效: {SUPABASE_URL}")
        print("请确保 URL 以 http:// 或 https:// 开头")
        return False
    
    # 打印配置信息（部分隐藏）
    print("配置信息:")
    print(f"  SUPABASE_URL: {SUPABASE_URL}")
    print(f"  SUPABASE_KEY: {SUPABASE_KEY[:20]}...")
    print(f"  SJTU_USERNAME: {ACCOUNT['username']}")
    return True


async def main():
    print("=" * 60)
    print("上海交大体育预约系统 - 自动更新版")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 验证配置
    if not validate_config():
        return
    
    print(f"目标场地: {[v['name'] for v in VENUES]}")
    print(f"账号: {ACCOUNT['username']}")
    print("=" * 60)

    # 步骤1: 登录获取session
    session_id = await login_and_get_session()

    if not session_id:
        print("❌ 登录失败，程序终止")
        return

    # 收集所有数据
    all_time_slots = []

    # 步骤2: 查询每个场地
    for venue in VENUES:
        print(f"\n{'='*60}")
        print(f"查询场地: {venue['name']}")
        print(f"{'='*60}")

        # 查询可预约日期
        dates = query_available_dates(session_id, venue['venue_id'], venue['field_type'])

        if not dates:
            print(f"❌ {venue['name']} 没有可预约日期")
            continue

        print(f"✅ 获取到 {len(dates)} 个可预约日期")

        # 查询每个日期的时段数据
        for i, date_info in enumerate(dates):
            date = date_info['date']
            date_id = date_info['dateId']

            # 添加查询间隔，避免请求过于频繁
            if i > 0:
                import time
                time.sleep(1)

            print(f"\n📅 查询 {date} 的时段...")
            fields_data = query_time_slots(
                session_id,
                venue['venue_id'],
                venue['field_type'],
                date,
                date_id
            )

            if fields_data:
                time_slots = format_time_slots_data(venue['venue_id'], fields_data, date)
                all_time_slots.extend(time_slots)

                # 打印可预约时段统计
                available_count = sum(1 for s in time_slots if s['status'] == '可预约')
                print(f"   ✅ 可预约时段: {available_count} 个")

    # 步骤3: 保存数据
    print(f"\n{'='*60}")
    print("保存数据")
    print(f"{'='*60}")

    # 保存JSON文件 (使用相对路径，兼容GitHub Actions)
    output_path = 'output/all_venues_booking_data.json'
    Path('output').mkdir(exist_ok=True)

    output_data = {
        'query_time': datetime.now().isoformat(),
        'total_slots': len(all_time_slots),
        'slots': all_time_slots
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON数据已保存到: {output_path}")

    # 保存到Supabase
    save_to_supabase(all_time_slots)

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
