from celery import shared_task
from .utils import StockDataParser


@shared_task
def update_stocks():
    parser = StockDataParser()
    parser.parse_files()

