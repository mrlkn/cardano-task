import json
import redis
from typing import List, Optional
from datetime import date
from app.csv_reader.models import Transaction
from app.csv_reader.serializers import TransactionSerializer


class CacheHandler:
    """
    CacheHandler is responsible for handling caching.
    """

    def __init__(self) -> None:
        self.redis = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

    def get_data_from_cache(
        self, cache_key: str
    ) -> Optional[List[TransactionSerializer]]:
        data = self.redis.get(cache_key)
        return (
            [
                TransactionSerializer.parse_raw(transaction_json)
                for transaction_json in json.loads(data)
            ]
            if data
            else None
        )

    def set_data_into_cache(
        self, cache_key: str, data: List[TransactionSerializer]
    ) -> None:
        serialized_data = [transaction.json() for transaction in data]
        self.redis.set(cache_key, json.dumps(serialized_data))


class DatabaseHandler:
    """
    DatabaseHandler is responsible for interacting with the database.
    """

    @staticmethod
    def is_data_in_db(csv_last_modified_date: date) -> bool:
        return (
            Transaction.select()
            .where(Transaction.csv_last_modified_date == csv_last_modified_date)
            .exists()
        )

    @staticmethod
    def fetch_data_from_db(csv_last_modified_date: date) -> List[TransactionSerializer]:
        return [
            TransactionSerializer.from_orm(transaction)
            for transaction in Transaction.select().where(
                Transaction.csv_last_modified_date == csv_last_modified_date
            )
        ]
