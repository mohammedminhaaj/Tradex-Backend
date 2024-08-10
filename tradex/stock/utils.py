import pandas as pd
import random
import string
from django.conf import settings
import os
from .models import Stock, StockDataAudit
from django.utils.crypto import get_random_string


class BaseStockData:
    def __init__(self):
        self._stock_data_dir = os.path.join(settings.MEDIA_ROOT, 'stock_data')
        os.makedirs(self._stock_data_dir, exist_ok=True)

    def _get_filenames(self):
        return [f for f in os.listdir(self._stock_data_dir) if f.endswith('.csv') and os.path.isfile(os.path.join(self._stock_data_dir, f))]


class StockNameGenerator:
    @staticmethod
    def generate_random_stock_name():
        length = random.choice([3, 4])
        return ''.join(random.choices(string.ascii_uppercase, k=length))


class StockPriceGenerator:
    @staticmethod
    def generate_random_stock_price(min_value: float, max_value: float):
        return round(random.uniform(min_value, max_value), 6)


class StockDataGenerator(BaseStockData):
    def __init__(self):
        super().__init__()

    def __get_existing_stock_names(self):
        return Stock.objects.values_list("name", flat=True)

    def generate_random_stocks(self, n: int = 10, min_price: float = 20.0, max_price: float = 100.0, use_existing_names: bool = False):
        if use_existing_names:
            unique_names = set(self.__get_existing_stock_names())
            stock_data = {
                "name": list(unique_names),
                "price": [StockPriceGenerator.generate_random_stock_price(min_price, max_price) for _ in range(len(unique_names))]
            }
        else:
            stock_data = {
                "name": [StockNameGenerator.generate_random_stock_name() for _ in range(n)],
                "price": [StockPriceGenerator.generate_random_stock_price(min_price, max_price) for _ in range(n)]
            }

        df = pd.DataFrame(stock_data)
        file_name = f'{get_random_string(length=10)}.csv'
        file_path = os.path.join(self._stock_data_dir, file_name)
        df.to_csv(file_path, index=False)
        return file_path

class StockDataParser(BaseStockData):
    def __init__(self):
        super().__init__()

    def __filter_unprocessed_files(self, filenames):
        processed_files = StockDataAudit.objects.filter(
            file_name__in=filenames).values_list("file_name", flat=True)
        return [file for file in filenames if file not in processed_files]

    def __create_stock_objects(self, df):
        return [Stock(name=row['name'], price=row['price']) for _, row in df.iterrows()]

    def __bulk_insert(self, stock_objects, audit_objects):
        if stock_objects:
            Stock.objects.bulk_create(stock_objects, batch_size=1000)
        if audit_objects:
            try:
                StockDataAudit.objects.bulk_create(audit_objects)
            except Exception as e:
                print(f"bulk create failed on audit data: {e}")

    def parse_files(self):
        files_to_process = self.__filter_unprocessed_files(
            self._get_filenames())
        stock_objects, audit_objects = [], []

        for file in files_to_process:
            file_path = os.path.join(self._stock_data_dir, file)
            df = pd.read_csv(file_path)
            stock_objects.extend(self.__create_stock_objects(df))
            audit_objects.append(StockDataAudit(file_name=file))

        self.__bulk_insert(stock_objects, audit_objects)