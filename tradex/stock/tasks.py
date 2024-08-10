from celery import shared_task
from .utils import StockDataParser

@shared_task
def update_stocks() -> None:
    """
    Celery task to update stocks by parsing stock data files.

    This task creates an instance of `StockDataParser` and calls its `parse_files` method
    to process stock data files. The task does not return any value and is executed asynchronously.
    """
    # Create an instance of StockDataParser
    parser = StockDataParser()
    
    # Call the parse_files method to process stock data
    parser.parse_files()
