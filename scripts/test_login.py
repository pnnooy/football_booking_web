#!/usr/bin/env python3
"""
登录流程测试: 不写Supabase, 只验证 [打开站点 → jAccount登录 → 取到数据]
成功登录后顺便保存 auth_state.json, 供爬虫后续使用
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sjtu_crawler_auto as crawler
from playwright.async_api import async_playwright

OUT = Path(__file__).parent.parent / 'output'


async def main():
    print("=== 测试开始 ===")
    if not crawler.validate_config():
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
            locale='zh-CN',
        )
        page = await context.new_page()

        try:
            # ─── 第1步: 打开站点, 匿名调API ───
            print("\n[1] 打开站点...")
            await page.goto(f'{crawler.BASE_URL}/pc/', timeout=30000)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            print(f"  URL: {page.url}")
            await page.screenshot(path=str(OUT / 'test_1_landing.png'))

            v = crawler.VENUES[0]
            test = await crawler.call_api(page,
                f'{crawler.BASE_URL}/manage/fieldDetail/queryFieldReserveSituationIsFull',
                {'id': v['venue_id'], 'feildType': v['field_type'], 'date': ''},
                "匿名检测")

            if test is not None:
                print("  匿名即可访问API, 无需登录")
            else:
                # ─── 第2步: jAccount 登录 ───
                print("\n[2] 需要登录, 开始jAccount流程...")
                btn = page.get_by_role("button", name="校内人员登录")
                if await btn.count() == 0:
                    print("  [ERR] 找不到'校内人员登录'按钮")
                    await page.screenshot(path=str(OUT / 'test_2_no_button.png'))
                    print("  页面文本:", (await page.locator('body').inner_text())[:300])
                    return
                await btn.click()
                await asyncio.sleep(5)
                await page.wait_for_load_state('networkidle')
                print(f"  点击登录后URL: {page.url}")
                await page.screenshot(path=str(OUT / 'test_2_jaccount_page.png'))

                if 'jaccount' not in page.url:
                    print("  [ERR] 未跳转到jAccount")
                    print("  页面文本:", (await page.locator('body').inner_text())[:300])
                    return

                # 填账号密码
                await page.fill('#input-login-user', crawler.ACCOUNT['username'])
                await page.fill('#input-login-pass', crawler.ACCOUNT['password'])
                await page.screenshot(path=str(OUT / 'test_3_filled.png'))

                ok = await crawler.jaccount_login(page)
                if not ok:
                    print("  [FAIL] OCR自动登录失败")
                    await page.screenshot(path=str(OUT / 'test_4_login_failed.png'))
                    print("  最终URL:", page.url)
                    print("  页面文本:", (await page.locator('body').inner_text())[:500])
                    return
                print("  登录成功! 当前URL:", page.url)
                await crawler.save_auth(context, page)

                # 回到体育网站
                await page.goto(f'{crawler.BASE_URL}/pc/', timeout=30000)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

            # ─── 第3步: 验证能取到数据 ───
            print("\n[3] 验证数据获取...")
            result = await crawler.call_api(page,
                f'{crawler.BASE_URL}/manage/fieldDetail/queryFieldReserveSituationIsFull',
                {'id': v['venue_id'], 'feildType': v['field_type'], 'date': ''},
                "查询日期")
            if not result or result.get('code') != 0:
                print(f"  [FAIL] 查询日期失败: {result}")
                await page.screenshot(path=str(OUT / 'test_5_query_failed.png'))
                return

            dates = result.get('data', [])
            print(f"  可查日期: {len(dates)} 个: {[d['date'] for d in dates]}")

            total, bookable = 0, 0
            for i, d in enumerate(dates):
                if i > 0:
                    await asyncio.sleep(0.5)
                r = await crawler.call_api(page,
                    f'{crawler.BASE_URL}/manage/fieldDetail/queryFieldSituation',
                    {'fieldType': v['field_type'], 'date': d['date'],
                     'venueId': v['venue_id'], 'dateId': d['dateId']}, d['date'])
                if r and r.get('code') == 0 and r.get('data'):
                    slots = crawler.format_slots(v['venue_id'], r['data'], d['date'])
                    n = sum(1 for s in slots if s['status'] == '可预约')
                    total += len(slots)
                    bookable += n
                    print(f"    {d['date']}: {n} 可预约 / 共 {len(slots)} 条")
                else:
                    print(f"    {d['date']}: [FAIL] 查询失败: {r}")

            print(f"\n=== 结果: {'PASS' if total > 0 else 'FAIL'} | 共{total}条, {bookable}条可预约 ===")

        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
