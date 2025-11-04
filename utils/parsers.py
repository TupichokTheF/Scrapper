from bs4 import BeautifulSoup
from playwright.async_api import expect
from abc import ABC, abstractmethod
from dataclasses import dataclass

from utils import RegistryWrapper

@dataclass(frozen=True)
class Product:
    name: str
    price: int
    image: str
    url: str

class SiteInterface(ABC):

    def __init__(self):
        self.content = None
        self.result = None

    async def execute(self, context, name_of_product):
        page = await context.new_page()
        await page.goto(self.url + name_of_product)
        locator = page.locator(self.css_selector)
        await expect(locator).to_be_visible(timeout=50000)
        self.content = await page.content()
        return self.parse_page()

    @abstractmethod
    def parse_page(self):
        pass


@RegistryWrapper()
class MVideo(SiteInterface):
    url = "https://www.mvideo.ru/product-list-page?q="
    css_selector = ".app"

    def parse_page(self):
        soup = BeautifulSoup(self.content, "html.parser")
        ls_items = soup.find_all("mvid-product-list")
        #print(ls_items)

@RegistryWrapper()
class Eldorado(SiteInterface):
    url = "https://www.eldorado.ru/search/catalog.php?q="
    css_selector = "#__next"

    def parse_page(self):
        soup = BeautifulSoup(self.content, "html.parser")
        ls_items = soup.find_all("li", {"class": "el1P"})
        self.result = [self.parse_one(item) for item in ls_items]

    def parse_one(self, item):
        item_data = []
        item_classes = [".el-P", ".elzY", ".elsB", ".elbv"]
        print(item.find('img', {"class": "elsB"}))

@RegistryWrapper()
class Citilink(SiteInterface):
    url = "https://www.citilink.ru/search/?text="
    css_selector = "#__next"

    def parse_page(self):
        pass

@RegistryWrapper()
class YaMarket(SiteInterface):
    url = "https://market.yandex.ru/search?text="
    css_selector = ".page"

    def parse_page(self):
        pass

@RegistryWrapper()
class Ozon(SiteInterface):
    url = "https://www.ozon.ru/search/?text="
    css_selector = "#__ozon"

    def parse_page(self):
        pass