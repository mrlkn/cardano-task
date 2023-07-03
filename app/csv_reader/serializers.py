from pydantic import BaseModel, constr, condecimal, validator
from datetime import datetime
from typing import Any


class TransactionSerializer(BaseModel):
    """
    TransactionSerializer is a Pydantic model used for validating and serializing
    transaction data.

    Attributes:
        transaction_uti (str): A unique identifier for the transaction.
        isin (str): International Securities Identification Number (12 characters).
        notional (Decimal): The notional amount (greater than 0).
        notional_currency (str): The currency code (3 characters).
        transaction_type (str): Type of transaction.
        transaction_datetime (datetime): The date and time of the transaction.
        rate (Decimal): Rate in range [0, 1].
        lei (str): Legal Entity Identifier (20 characters).
    """

    transaction_uti: constr(min_length=1, max_length=100)
    isin: constr(min_length=12, max_length=12)
    notional: condecimal(gt=0)
    notional_currency: constr(min_length=3, max_length=3)
    transaction_type: constr(min_length=1, max_length=10)
    transaction_datetime: datetime
    rate: condecimal(ge=0, le=1)
    lei: constr(min_length=20, max_length=20)

    class Config:
        orm_mode = True

    @validator("transaction_datetime", pre=True)
    def parse_datetime(cls, value: Any) -> datetime:
        """
        Validates and parses the transaction datetime string.

        Parameters:
            value (Any): Value to validate

        Returns:
            datetime: The parsed datetime.

        Raises:
            ValueError: If the input value is not in the expected format.
        """
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise ValueError("Invalid datetime format")
