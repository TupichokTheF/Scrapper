from bs4 import BeautifulSoup
from playwright.async_api import expect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from aiohttp import ClientSession
import json
from .request_params.MVideo import GET_product_ids, POST_list_products, GET_product_prices
import time, asyncio

from utils import RegistryWrapper, Logger

@dataclass(frozen=True)
class Product:
    name: str
    price: int
    image: str
    shop: str
    url: str = None

class SiteInterface(ABC):
    _url = None
    _css_selector = None

    def __init__(self):
        self.content = None
        self.page = None

    async def execute(self, context, name_of_product):
        await self.load_page(context, name_of_product)
        self.content = await self.page.content()
        return self.parse_page()

    async def load_page(self, context, name_of_product):
        self.page = await context.new_page()
        await self.page.goto(self._url.format(name_of_product))
        locator = self.page.locator(self._css_selector)
        await expect(locator).to_be_visible(timeout=50000)

    @abstractmethod
    def parse_page(self):
        pass


@RegistryWrapper()
class MVideo:

    async def execute(self, _, name_of_product):
        async with ClientSession() as session:
            product_ids = await self.get_product_ids(session, name_of_product)
            products, product_prices = await asyncio.gather(*[self.get_products(session, product_ids), self.get_product_prices(session, product_ids)])
        return [Product(product['name'], price['price']['salePrice'], "https://img.mvideo.ru/" + product['image'], "МВидео")
                for product, price in zip(products, product_prices)]

    @Logger(sync=False)
    async def get_product_ids(self, session, name_of_product):
        GET_product_ids.PARAMS["query"] = name_of_product
        async with session.get(GET_product_ids.URL, params=GET_product_ids.PARAMS,
                               cookies=GET_product_ids.COOKIES,
                               headers=GET_product_ids.HEADERS) as response:
            res = await response.read()
            data = json.loads(res)

        return data["body"]["products"]

    @Logger(sync=False)
    async def get_products(self, session, product_ids):
        POST_list_products.JSON_DATA['productIds'] = product_ids
        async with session.post(POST_list_products.URL, params=GET_product_ids.PARAMS,
                                cookies=GET_product_ids.COOKIES,
                                headers=GET_product_ids.HEADERS,
                                json=POST_list_products.JSON_DATA) as response:
            result = await response.read()
            data = json.loads(result)

        return sorted(data["body"]["products"], key= lambda x: x['productId'])

    @Logger(sync=False)
    async def get_product_prices(self, session, product_ids):
        GET_product_prices.PARAMS['productIds'] = ','.join(product_ids)
        async with session.get(GET_product_prices.URL, params=GET_product_prices.PARAMS,
                               cookies=GET_product_ids.COOKIES,
                               headers=GET_product_ids.HEADERS) as response:
            res = await response.read()
            data = json.loads(res)

        return sorted(data["body"]["materialPrices"], key=lambda x: x['productId'])


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

    @Logger(sync=True)
    def parse_one(self, item):
        try:
            item_tags = item.findChildren("div", recursive=False)
            image = item_tags[0].find("img")["src"]
            name = item_tags[1].find("a").contents[0]
            price = item_tags[2].find("span").contents[0]
            url = item_tags[0].find("a")["href"]
            return Product(name, price, image, "Эльдорадо", url)
        except Exception as e:
            #logging.exception(type(e).__name__)
            return None

@RegistryWrapper()
class Citilink(SiteInterface):
    _url = "https://www.citilink.ru/search/?text={0}"
    _css_selector = "[data-meta-name=ProductListLayout]"

    @Logger(sync=False)
    async def load_page(self, context, name_of_product):
        await super().load_page(context, name_of_product)
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await self.page.wait_for_timeout(5000)

    @Logger(sync=True)
    def parse_page(self):
        soup = BeautifulSoup(self.content, "html.parser")
        elements = (soup.find("div", {"data-meta-name": "ProductListLayout"})
              .find("section")
              .findChildren("div", recursive = False)[1]
              .findChildren("div", recursive = False)[1]
              .findChildren("div", recursive = False))
        return [self.parse_one_product(element) for element in elements]

    @Logger(sync=True)
    def parse_one_product(self, element):
        tags = element.find("div").find("div").findChildren("div", recursive = False)
        image = tags[1].find("img")["src"]
        name = tags[1].findChildren("div", recursive = False)[2].find("a").get_text()
        url = "https://www.citilink.ru/" + tags[1].findChildren("div", recursive = False)[2].find("a")["href"]
        price = tags[4].findChildren("div", recursive = False)[1].find("div").get_text()
        pr = Product(name, price, image, "Ситилинк", url)
        return pr

@RegistryWrapper()
class YaMarket(SiteInterface):
    _url = "https://market.yandex.ru/search?text={0}"
    _css_selector = ".page"

    def parse_page(self):
        soup = BeautifulSoup(self.content, "html.parser")
        elements = (soup.find("div", {"data-auto": "SerpList"}).findChildren("div", recursive = False))
        return [self.parse_one(element) for element in elements]

    @Logger(sync=True)
    def parse_one(self, element):
        tags = (element.find("div", {"data-auto-themename": "listDetailed"})
                .find("div")
                .findChildren("div", recursive = False))
        image = tags[0].find("img")["src"]
        name = tags[1].find("div").get_text()
        url = "https://market.yandex.ru" + tags[1].find("div").find("a")["href"]
        price = tags[2].find("span", {"data-auto": "snippet-price-current"}).find("span").contents[0]
        return Product(name, price, image, "ЯМаркет", url)



@RegistryWrapper()
class Ozon(SiteInterface):
    _url = "https://www.ozon.ru/search/?text={0}"
    _css_selector = "#__ozon"

    def parse_page(self):
        pass