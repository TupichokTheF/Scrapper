from utils import sync_timer

from abc import abstractmethod, ABC
import csv

class WriterInterface(ABC):

    @abstractmethod
    def write_to_file(self):
        pass

class CsvWriter(WriterInterface):

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
            for product in shop_products:
                if product:
                    yield product.transform_to_list()

FILE_WRITERS = {
    "CSV": CsvWriter,
}