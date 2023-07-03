import csv
import logging
import os
from datetime import datetime
from app.csv_reader.serializers import TransactionSerializer
from typing import List


class CSVReader:
    """
    CSVReader is a class for reading a CSV file containing transactions.

    Attributes:
        file_path (str): The path to the CSV file.
        delimiter (str): The delimiter used in the CSV file.
    """

    def __init__(self, file_path: str, delimiter: str = ",") -> None:
        self.file_path = file_path
        self.delimiter = delimiter

    def get_csv_last_modified_date(self) -> datetime.date:
        return datetime.fromtimestamp(os.path.getmtime(self.file_path)).date()

    def read_csv(self) -> List[TransactionSerializer]:
        logging.info("Reading data from CSV")
        data = []
        with open(self.file_path, "r") as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            for row in reader:
                transaction = TransactionSerializer(**row)
                data.append(transaction)
        return data
