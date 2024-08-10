import os
import random
import string
import pandas as pd
from django.conf import settings
from django.utils.crypto import get_random_string
from typing import List, Dict, Optional
from .models import Stock, StockDataAudit


class BaseStockData:
    """
    Base class to handle common functionalities related to stock data files.
    """

    def __init__(self):
        """
        Initialize the base stock data directory and ensure it exists.
        """
        self._stock_data_dir = os.path.join(settings.MEDIA_ROOT, 'stock_data')
        os.makedirs(self._stock_data_dir, exist_ok=True)

    def _get_filenames(self) -> List[str]:
        """
        Get a list of filenames in the stock data directory that are CSV files.

        Returns:
            List[str]: List of filenames with '.csv' extension.
        """
        return [
            f for f in os.listdir(self._stock_data_dir)
            if f.endswith('.csv') and os.path.isfile(os.path.join(self._stock_data_dir, f))
        ]


class StockNameGenerator:
    """
    A utility class to generate random stock names.
    """

    @staticmethod
    def generate_random_stock_name() -> str:
        """
        Generate a random stock name with 3 or 4 uppercase characters.

        Returns:
            str: Random stock name.
        """
        length = random.choice([3, 4])
        return ''.join(random.choices(string.ascii_uppercase, k=length))


class StockPriceGenerator:
    """
    A utility class to generate random stock prices.
    """

    @staticmethod
    def generate_random_stock_price(min_value: float, max_value: float) -> float:
        """
        Generate a random stock price between min_value and max_value.

        Args:
            min_value (float): Minimum price.
            max_value (float): Maximum price.

        Returns:
            float: Random stock price rounded to 6 decimal places.
        """
        return round(random.uniform(min_value, max_value), 6)


class StockDataGenerator(BaseStockData):
    """
    A class for generating and saving stock data to CSV files.
    """

    def __init__(self):
        """
        Initialize StockDataGenerator.
        """
        super().__init__()

    def __get_existing_stock_names(self):
        """
        Retrieve existing stock names from the database.

        Returns:
            List[str]: List of stock names.
        """
        return Stock.objects.values_list("name", flat=True)

    def generate_random_stocks(
        self,
        n: int = 10,
        min_price: float = 20.0,
        max_price: float = 100.0,
        use_existing_names: bool = False
    ) -> str:
        """
        Generate random stocks and save them to a CSV file.

        Args:
            n (int): Number of stocks to generate.
            min_price (float): Minimum stock price.
            max_price (float): Maximum stock price.
            use_existing_names (bool): Whether to use existing stock names.

        Returns:
            str: File path of the saved CSV file.
        """
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
        return file_name


class StockDataParser(BaseStockData):
    """
    A class for parsing stock data from CSV files and saving them to the database.
    """

    def __init__(self):
        """
        Initialize StockDataParser.
        """
        super().__init__()

    def __filter_unprocessed_files(self, filenames: List[str]) -> List[str]:
        """
        Filter out files that have already been processed.

        Args:
            filenames (List[str]): List of filenames to filter.

        Returns:
            List[str]: List of unprocessed filenames.
        """
        processed_files = StockDataAudit.objects.filter(
            file_name__in=filenames).values_list("file_name", flat=True)
        return [file for file in filenames if file not in processed_files]

    def __create_stock_objects(self, df: pd.DataFrame) -> List[Stock]:
        """
        Create a list of Stock objects from the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing stock data.

        Returns:
            List[Stock]: List of Stock objects.
        """
        return [Stock(name=row['name'], price=row['price']) for _, row in df.iterrows()]

    def __bulk_insert(self, stock_objects: List[Stock], audit_objects: List[StockDataAudit]) -> None:
        """
        Bulk insert stock and audit objects into the database.

        Args:
            stock_objects (List[Stock]): List of Stock objects to insert.
            audit_objects (List[StockDataAudit]): List of StockDataAudit objects to insert.
        """
        if stock_objects:
            Stock.objects.bulk_create(stock_objects, batch_size=1000)
        if audit_objects:
            try:
                StockDataAudit.objects.bulk_create(audit_objects)
            except Exception as e:
                print(f"Bulk create failed on audit data: {e}")

    def parse_files(self) -> None:
        """
        Parse unprocessed CSV files and save stock data to the database.
        """
        files_to_process = self.__filter_unprocessed_files(
            self._get_filenames())
        stock_objects, audit_objects = [], []

        for file in files_to_process:
            file_path = os.path.join(self._stock_data_dir, file)
            df = pd.read_csv(file_path)
            stock_objects.extend(self.__create_stock_objects(df))
            audit_objects.append(StockDataAudit(file_name=file))

        self.__bulk_insert(stock_objects, audit_objects)
