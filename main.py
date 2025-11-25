import asyncio

from playwright.async_api import async_playwright, ViewportSize
from playwright_stealth import Stealth

from utils import RegistryWrapper, async_timer, file_writers

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

@async_timer
async def executer(name_of_product_):
    res = []
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=USER_AGENT, viewport=ViewportSize(width=1920, height=1080))
        sites = RegistryWrapper.take_sites()
        pending = [asyncio.create_task(site.execute(context, name_of_product_)) for site in sites]

        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for done_task in done:
                if not done_task.exception():
                    res.append(done_task.result())
    return res

async def main():
    name_of_product = '+'.join(input().split())
    parsed_elements = await executer(name_of_product)
    writer = file_writers.FILE_WRITERS["CSV"]
    writer = writer(parsed_elements)
    writer.write_to_file()

if __name__ == '__main__':
    asyncio.run(main())

