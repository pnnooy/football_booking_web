"""
保存登录态: 打开浏览器让用户手动完成jAccount登录, 然后保存cookies到文件
之后 sjtu_crawler_auto.py 可以直接加载已保存的cookies, 跳过登录步骤
"""
import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

BASE_URL = 'https://sports.sjtu.edu.cn'
AUTH_FILE = Path(__file__).parent.parent / 'output' / 'auth_state.json'


async def main():
    print("=" * 60)
    print("登录态保存工具")
    print("会打开Chrome浏览器,请在浏览器中手动登录")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='zh-CN',
        )
        page = await context.new_page()

        # 打开体育网站
        print("\n正在打开体育网站...")
        await page.goto(f'{BASE_URL}/pc/', timeout=30000)
        await page.wait_for_load_state('networkidle')

        print("\n" + "=" * 60)
        print("请在浏览器中手动登录!")
        print("(点击校内人员登录 → 输入jAccount和验证码 → 登录)")
        print("脚本会自动检测登录完成...")
        print("=" * 60)

        # 等待用户完成登录 (检测URL回到体育网站)
        for i in range(120):  # 最多等2分钟
            await asyncio.sleep(1)
            current_url = page.url
            # 登录成功标志: 回到sports.sjtu.edu.cn且不是jAccount页面
            if 'sports.sjtu.edu.cn' in current_url and 'jaccount' not in current_url:
                # 再等2秒确保页面加载完成
                await asyncio.sleep(2)
                # 检查是否有用户信息(登录成功标志)
                try:
                    has_login = await page.evaluate("""
                    () => {
                        // 检查是否有登录用户信息
                        return document.body.innerText.includes('退出') ||
                               document.querySelector('[class*="user"]') !== null ||
                               document.querySelector('[class*="avatar"]') !== null;
                    }
                    """)
                except Exception:
                    has_login = False

                if has_login or i > 20:
                    print(f"\n检测到登录完成! URL: {current_url}")
                    break

        if 'jaccount' in page.url:
            print("\n还在jAccount页面, 登录可能未完成")
            print("浏览器保持打开, 请完成登录后手动关闭浏览器")
            await asyncio.sleep(120)  # 再等2分钟

        current_url = page.url
        print(f"当前URL: {current_url}")

        # 保存所有cookies
        cookies = await context.cookies()
        print(f"获取到 {len(cookies)} 个cookies")

        # 保存
        auth_data = {
            'cookies': cookies,
            'url': current_url,
        }
        Path(AUTH_FILE).parent.mkdir(exist_ok=True)
        import json
        with open(AUTH_FILE, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f, ensure_ascii=False, indent=2)

        # 检查JSESSIONID是否存在(登录成功的标志)
        has_session = any(c['name'] == 'JSESSIONID' for c in cookies)
        if has_session:
            print(f"\nOK 登录态已保存到: {AUTH_FILE}")
            print(f"包含 {len(cookies)} 个cookies (含JSESSIONID)")
            print("现在可以运行 sjtu_crawler_auto.py")
        else:
            print("\nWARN 未检测到JSESSIONID, 登录可能失败")
            print("请确保已在浏览器中完成登录,然后重新运行此脚本")

        # 保持浏览器打开5秒让用户看到结果
        print("\n5秒后关闭浏览器...")
        await asyncio.sleep(5)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
