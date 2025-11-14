from bs4 import BeautifulSoup
from playwright.async_api import expect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from aiohttp import ClientSession
import json
from .request_params.MVideo import GET_product_ids, POST_list_products, GET_product_prices
import time, asyncio

from utils import RegistryWrapper

@dataclass(frozen=True)
class Product:
    name: str
    price: int
    image: str
    url: str = None

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
class MVideo:

    async def execute(self, _, name_of_product):
        async with ClientSession() as session:
            product_ids = await self.get_product_ids(session, name_of_product)
            products, product_prices = await asyncio.gather(*[self.get_products(session, product_ids), self.get_product_prices(session, product_ids)])
        return [Product(product['name'], price['price']['salePrice'], "https://img.mvideo.ru/" + product['image'])
                for product, price in zip(products, product_prices)]

    async def get_product_ids(self, session, name_of_product):
        try:
            GET_product_ids.PARAMS["query"] = name_of_product
            async with session.get(GET_product_ids.URL, params=GET_product_ids.PARAMS,
                                   cookies=GET_product_ids.COOKIES,
                                   headers=GET_product_ids.HEADERS) as response:
                res = await response.read()
                data = json.loads(res)

            return data["body"]["products"]
        except Exception as e:
            print(f"Get_Product_ids: {e}")

    async def get_products(self, session, product_ids):
        try:
            POST_list_products.JSON_DATA['productIds'] = product_ids
            async with session.post(POST_list_products.URL, params=GET_product_ids.PARAMS,
                                    cookies=GET_product_ids.COOKIES,
                                    headers=GET_product_ids.HEADERS,
                                    json=POST_list_products.JSON_DATA) as response:
                result = await response.read()
                data = json.loads(result)

            return sorted(data["body"]["products"], key= lambda x: x['productId'])
        except Exception as e:
            print(f"Get_Products: {e}")

    async def get_product_prices(self, session, product_ids):
        try:
            GET_product_prices.PARAMS['productIds'] = ','.join(product_ids)
            async with session.get(GET_product_prices.URL, params=GET_product_prices.PARAMS,
                                   cookies=GET_product_ids.COOKIES,
                                   headers=GET_product_ids.HEADERS) as response:
                res = await response.read()
                data = json.loads(res)

            return sorted(data["body"]["materialPrices"], key=lambda x: x['productId'])
        except Exception as e:
            print(f"Get_Product_Pricces: {e}")


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
        soup = BeautifulSoup(self.content, "html.parser")
        elements = (soup.find("div", {"data-meta-name": "ProductListLayout"})
              .find("section")
              .findChildren("div", recursive = False)[1]
              .findChildren("div", recursive = False)[1]
              .findChildren("div", recursive = False))
        return [self.parse_one_product(element) for element in elements]

    def parse_one_product(self, element):
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