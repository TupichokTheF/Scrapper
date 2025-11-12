from bs4 import BeautifulSoup
from playwright.async_api import expect
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

from utils import RegistryWrapper

@dataclass(frozen=True)
class Product:
    name: str
    price: int
    image: str
    url: str

class SiteInterface(ABC):
    _url = None
    _css_selector = None

    def __init__(self):
        self.content = None

    async def execute(self, context, name_of_product):
        page = await context.new_page()
        await page.goto(self._url.format(name_of_product))
        locator = page.locator(self._css_selector)
        await expect(locator).to_be_visible(timeout=50000)
        self.content = await page.content()
        return self.parse_page()

    @abstractmethod
    def parse_page(self):
        pass


@RegistryWrapper()
class MVideo(SiteInterface):
    _url = "https://www.mvideo.ru/product-list-page?q={0}"
    _css_selector = ".app"

    def parse_page(self):
        soup = BeautifulSoup(self.content, "html.parser")
        ls_items = soup.findAll("div", {"class": "product-cards-row"})
        print(ls_items)

@RegistryWrapper()
class Eldorado(SiteInterface):
    _url = "https://www.eldorado.ru/search/catalog.php?q={0}"
    _css_selector = "#__next"

    def parse_page(self):
        soup = BeautifulSoup(self.content, "html.parser")
        ls_items = (soup.find("div", {"id": "listing-container"})
                    .find("ul")
                    .findChildren("li", recursive = False))
        result = [self.parse_one(item) for item in ls_items]
        return result

    def parse_one(self, item):
        try:
            item_tags = item.findChildren("div", recursive=False)
            image = item_tags[0].find("img")["src"]
            name = item_tags[1].find("a").contents[0]
            price = item_tags[2].find("span").contents[0]
            url = item_tags[0].find("a")["href"]
            return Product(name, price, image, url)
        except Exception as e:
            #logging.exception(type(e).__name__)
            return None

@RegistryWrapper()
class Citilink(SiteInterface):
    _url = "https://www.citilink.ru/search/?text={0}"
    _css_selector = "#__next"

    def parse_page(self):
        pass

@RegistryWrapper()
class YaMarket(SiteInterface):
    _url = "https://market.yandex.ru/search?text={0}"
    _css_selector = ".page"

    def parse_page(self):
        pass

@RegistryWrapper()
class Ozon(SiteInterface):
    _url = "https://www.ozon.ru/search/?text={0}"
    _css_selector = "#__ozon"

    def parse_page(self):
        pass