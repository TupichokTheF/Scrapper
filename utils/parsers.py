from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, expect
from abc import ABC, abstractmethod

from utils import RegistryWrapper

class SiteInterface(ABC):

    def __init__(self):
        self.content = None

    async def execute(self, context, name_of_product):
        page = await context.new_page()
        await page.goto(self.take_url() + name_of_product)
        locator = page.locator("body")
        await expect(locator).to_be_visible(timeout=50000)
        self.content = await page.content()
        self.content = BeautifulSoup(self.content, 'html.parser')
        return self.parse_page()

    @abstractmethod
    def take_url(self):
        pass

    @abstractmethod
    def parse_page(self):
        pass


@RegistryWrapper()
class MVideo(SiteInterface):

    def take_url(self):
        return "https://www.mvideo.ru/product-list-page?q="

    def parse_page(self):
        pass

@RegistryWrapper()
class Eldorado(SiteInterface):

    def take_url(self):
        return "https://www.eldorado.ru/search/catalog.php?q="

    def parse_page(self):
        pass

@RegistryWrapper()
class Citilink(SiteInterface):

    def take_url(self):
        return "https://www.citilink.ru/search/?text="

    def parse_page(self):
        pass

@RegistryWrapper()
class YaMarket(SiteInterface):

    def take_url(self):
        return "https://market.yandex.ru/search?text="

    def parse_page(self):
        pass

@RegistryWrapper()
class Ozon(SiteInterface):

    def take_url(self):
        return "https://www.ozon.ru/search/?text="

    def parse_page(self):
        pass