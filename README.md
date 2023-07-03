# Cardano Task - CSV Processing and Data Enrichment API

## Table of Contents
- [Running the Service](#running-the-service)
- [Project Overview](#project-overview)
- [CSV Reader](#csv-reader)
- [Models and Serializers](#models-and-serializers)
- [Data Enrichment](#data-enrichment)
- [Database Interaction](#database-interaction)
- [Caching Mechanism](#caching-mechanism)
- [API Endpoints](#api-endpoints)

## Running the Service

To run the service make sure you created .env with example 
```text
POSTGRES_USER=db
POSTGRES_PASSWORD=db
POSTGRES_DB=db
POSTGRES_HOST=cardano_db
POSTGRES_PORT=5432
```
Then just run 
```sh
docker-compose build
docker-compose up
```

## Project Overview

Service extracts data from CSV, stores it in the cache and in the database.

Depending on the request there are few flows.

- If latest CSV is in the cache, return it from the cache
- If latest CSV is not in the cache, but in database, return it from the database
- Else just read from CSV again

## CSV Reader

The CSV reader is responsible for reading transaction data from a CSV file. It's implemented in the `CSVReader` class. The class takes the file path as an argument and reads the contents. It uses Python's built-in `csv` module.

## Database Interaction

The `DatabaseHandler` class handles interactions with the database. It has methods to check whether data is already available in the database for a given date, to fetch data from the database, and to save data into the database. The project uses PostgreSQL as the database and [Peewee](https://docs.peewee-orm.com/en/latest/) as the ORM. 

## Caching Mechanism

The `CacheHandler` class manages caching. It uses `Redis` as the caching backend. When the service reads data from the CSV file, it caches the data in Redis with the last modified date of the file as the key. The next time the service needs the data, it first checks if the cache has data for the last modified date of the file. If so, it uses the cached data instead of reading the file again.

## Models and Serializers

### Models

`Transaction` model is an ORM model that represents the database table where the transactions will be stored. This model is defined using [Peewee](https://docs.peewee-orm.com/en/latest/), a simple Python ORM.

### Serializers

The `TransactionSerializer` class is a Pydantic model used for validating and serializing transaction data. It ensures that the data read from the CSV file conforms to the expected structure.

## Data Enrichment

The `AsyncAPIClient` class is responsible for enriching the transaction data. This class makes asynchronous HTTP requests to an external API to fetch additional data using the `httpx` library. This additional data is then combined with the transaction data read from the CSV file.

Used a strategy to create cost calculation logics which can be found in the `cost_strategy_pattern.py`


## API Endpoints

 `/lei-records` returns the enriched transaction data.

- `GET /lei-records`: Fetches the enriched transaction data. This endpoint internally manages data retrieval from the cache, database, or CSV file, enriches the data by making requests to an external API, and returns the enriched data.

## Linting
Used [Black](https://github.com/psf/black) as a formatter and [Mypy](https://mypy-lang.org/) as a type hinting tool.

## Devs notes

Unfortunately, last couple of weeks were unbelievably hectic and tiring therefore completing this task took longer than I expected. 

Again unfortunately, I can not say I am 100% satisfied with the outcome, but I had finish it. So it's **missing tests** and I believe client could have better implementation.

