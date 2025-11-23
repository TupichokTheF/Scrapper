import asyncio, csv, dataclasses, functools, multiprocessing
from asyncio import FIRST_EXCEPTION, FIRST_COMPLETED
from concurrent.futures import ProcessPoolExecutor

from playwright.async_api import async_playwright, ViewportSize
from playwright_stealth import Stealth

from utils import RegistryWrapper, async_timer, sync_timer

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
            done, pending = await asyncio.wait(pending, return_when=FIRST_COMPLETED)
            for done_task in done:
                if not done_task.exception():
                    res.append(done_task.result())
    return res

class CsvWriter:

    def __init__(self, elements):
        self.elements = elements

    @sync_timer
    def write_to_file(self):
        with open("data.csv", 'w', encoding="utf-8") as file:
            csv_writer = csv.writer(file)
            for row in self.take_products():
                csv_writer.writerow(row)

    def take_products(self):
        for shop_products in self.elements:
            yield from self.dataclass_to_list(shop_products)

    def dataclass_to_list(self, shop_products):
        for product in shop_products:
            if product:
                product_fields = dataclasses.fields(product)
                yield [getattr(product, field.name) for field in product_fields]

async def main():
    name_of_product = '+'.join(input().split())
    parsed_elements = await executer(name_of_product)
    writer = CsvWriter(parsed_elements)
    writer.write_to_file()

if __name__ == '__main__':
    asyncio.run(main())

