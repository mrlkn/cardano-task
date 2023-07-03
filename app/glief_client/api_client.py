import aiohttp
import logging
import asyncio
from typing import List, Iterable, Optional

from app.csv_reader.models import Transaction
from app.glief_client.models import LeiRecord


class AsyncAPIClient:
    def __init__(
        self, base_url: str, headers: Optional[dict] = None, timeout: int = 10
    ):
        """
        Initializes the Async API Client.

        Parameters:
            base_url (str): The base URL for the API.
            headers (dict, optional): Headers to use for the API request.
            timeout (int, optional): The timeout for the API request in seconds.
        """
        self.base_url = base_url
        self.headers = headers or {"Accept": "application/json"}
        self.timeout = timeout

    def build_url(self, lei_codes: Iterable[str], page: int = 1) -> str:
        """
        Builds the URL for the API request.

        Parameters:
            lei_codes (Iterable[str]): The LEI codes to filter by.
            page (int, optional): The page number to fetch.

        Returns:
            str: The built URL.
        """
        lei_codes_query = ",".join(lei_codes)
        return f"{self.base_url}/api/v1/lei-records?filter[lei]={lei_codes_query}&page[number]={page}"

    async def fetch_page(self, session, url: str) -> List[dict]:
        """
        Fetches a page of data from the API.

        Parameters:
            session (aiohttp.ClientSession): The aiohttp client session.
            url (str): The URL to fetch data from.

        Returns:
            List[dict]: The list of records from the fetched page, or None if request failed.
        """
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        try:
            async with session.get(
                url, headers=self.headers, timeout=timeout
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.warning(
                        f"Received status code {response.status} for url: {url}"
                    )
                    return None
        except Exception as e:
            logging.error(f"An error occurred while fetching the page: {str(e)}")
            return None

    async def process_page_data(
        self, page_data: List[dict], transactions_map: dict
    ) -> List[LeiRecord]:
        """
        Processes the data fetched from a page.

        Parameters:
            page_data (List[dict]): The data from the fetched page.
            transactions_map (dict): A mapping of LEI codes to transactions to access the notional and rate.

        Returns:
            List[LeiRecord]: A list of processed LEI records.
        """
        lei_records = []
        for item in page_data:
            lei_code = item.get("attributes", {}).get("lei")
            if lei_code and lei_code in transactions_map:
                notional = transactions_map[lei_code].notional
                rate = transactions_map[lei_code].rate
                lei_record = LeiRecord(**item)
                transaction_costs = lei_record.calculate_transaction_costs(
                    notional, rate
                )
                lei_record.transaction_cost = transaction_costs
                lei_records.append(lei_record)
        return lei_records

    async def fetch_all_pages_for_transactions(
        self, session, transactions: Iterable[Transaction]
    ) -> List[LeiRecord]:
        """
        Fetches and processes all pages for given transactions.

        Parameters:
            session (aiohttp.ClientSession): The aiohttp client session.
            transactions (Iterable[Transaction]): The transactions to fetch pages for.

        Returns:
            List[LeiRecord]: A list of processed LEI records.
        """
        transactions_map = {t.lei: t for t in transactions}

        first_page = await self.fetch_page(
            session, self.build_url(transactions_map.keys(), page=1)
        )
        if not first_page:
            return []

        total_pages = first_page["meta"]["pagination"]["lastPage"]
        tasks = [
            self.fetch_page(session, self.build_url(transactions_map.keys(), page))
            for page in range(2, total_pages + 1)
        ]

        pages = await asyncio.gather(*tasks)
        pages.insert(0, first_page)

        lei_records = []
        for page in pages:
            if page:
                records = await self.process_page_data(page["data"], transactions_map)
                lei_records.extend(records)

        return lei_records

    async def make_request(
        self, transactions: Iterable[Transaction], batch_size: int = 10
    ) -> List[LeiRecord]:
        """
        Makes an API request for the given transactions.

        Parameters:
            transactions (Iterable[Transaction]): The transactions to make request for.
            batch_size (int, optional): The batch size for processing transactions.

        Returns:
            List[LeiRecord]: A list of LEI records.
        """
        async with aiohttp.ClientSession() as session:
            lei_records = []

            transactions_list = list(transactions)
            for i in range(0, len(transactions_list), batch_size):
                batch_transactions = transactions_list[i : i + batch_size]

                batch_lei_records = await self.fetch_all_pages_for_transactions(
                    session, batch_transactions
                )

                lei_records.extend(batch_lei_records)

            return lei_records
