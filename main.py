import asyncio
from asyncio import FIRST_EXCEPTION
from playwright.async_api import async_playwright, ViewportSize
from playwright_stealth import Stealth

from utils import RegistryWrapper, async_timer

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

@async_timer
async def executer(name_of_product_):
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=USER_AGENT, viewport=ViewportSize(width=1920, height=1080))
        sites = RegistryWrapper.take_sites()
        pending = [asyncio.create_task(site.execute(context, name_of_product_)) for site in sites]

        while pending:
            done, pending = await asyncio.wait(pending, return_when=FIRST_EXCEPTION)
            for done_task in done:
                if not done_task.exception():
                    print(done_task)
        await asyncio.sleep(100)

if __name__ == '__main__':
    name_of_product = '+'.join(input().split())
    asyncio.run(executer(name_of_product))
