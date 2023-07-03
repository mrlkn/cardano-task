from fastapi import APIRouter, Depends, HTTPException

from app.csv_reader.data_handlers import CacheHandler, DatabaseHandler
from app.glief_client.api_client import AsyncAPIClient
from app.csv_reader.reader import CSVReader

router = APIRouter()


def get_csv_data():
    try:
        csv_reader = CSVReader("app/csv_reader/input_dataset.csv")
        cache_handler = CacheHandler()
        db_handler = DatabaseHandler()

        csv_last_modified_date = csv_reader.get_csv_last_modified_date()

        data = cache_handler.get_data_from_cache(str(csv_last_modified_date))
        if data:
            return data

        if db_handler.is_data_in_db(csv_last_modified_date):
            data = db_handler.fetch_data_from_db(csv_last_modified_date)
            cache_handler.set_data_into_cache(str(csv_last_modified_date), data)
            return data

        data = csv_reader.read_csv()
        cache_handler.set_data_into_cache(str(csv_last_modified_date), data)
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing CSV data")


def get_api_client() -> AsyncAPIClient:
    return AsyncAPIClient("https://api.gleif.org")


@router.get("/lei-records", tags=["LEI Records"])
async def get_lei_records(
    data: list = Depends(get_csv_data), client: AsyncAPIClient = Depends(get_api_client)
):
    try:
        lei_records = await client.make_request(data)
        return lei_records
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching LEI records")
