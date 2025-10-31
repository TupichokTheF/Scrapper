from playwright.async_api import async_playwright, expect
from abc import ABC, abstractmethod

from utils import RegistryWrapper

class SiteInterface(ABC):

    def __init__(self):
        self._name_of_product = None

    @property
    def name_of_product(self):
        return self._name_of_product

    @name_of_product.setter
    def name_of_product(self, value):
        self._name_of_product = value

    @abstractmethod
    async def execute(self, context):
        pass


@RegistryWrapper()
class MVideo(SiteInterface):

    async def execute(self, context):
        page = await context.new_page()
        await page.goto(f"https://www.mvideo.ru/product-list-page?q={self._name_of_product}")
        locator = page.locator(".app")
        await expect(locator).to_be_visible(timeout=50000)
        content = await page.content()
        return content


@RegistryWrapper()
class Eldorado(SiteInterface):

    async def execute(self, context):
        page = await context.new_page()
        await page.goto(f"https://www.eldorado.ru/search/catalog.php?q={self._name_of_product}&utf")
        locator = page.locator("#__next")
        await expect(locator).to_be_visible(timeout=50000)
        content = await page.content()
        return content

@RegistryWrapper()
class Citilink(SiteInterface):

    async def execute(self, context):
        page = await context.new_page()
        await page.goto(f"https://www.citilink.ru/search/?text={self._name_of_product}")
        locator = page.locator("#__next")
        await expect(locator).to_be_visible(timeout=50000)
        content = await page.content()
        return content

@RegistryWrapper()
class YaMarket(SiteInterface):

    async def execute(self, context):
        page = await context.new_page()
        await page.goto(f"https://market.yandex.ru/search?text={self._name_of_product}")
        locator = page.locator(".page")
        await expect(locator).to_be_visible(timeout=50000)
        content = await page.content()
        return content

@RegistryWrapper()
class Ozon(SiteInterface):

    async def execute(self, context):
        page = await context.new_page()
        await page.goto(f"https://www.ozon.ru/search/?text={self._name_of_product}")
        locator = page.locator("#__ozon")
        await expect(locator).to_be_visible(timeout=50000)
        content = await page.content()
        return content