from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict


class TransactionCostStrategy(ABC):
    """
    TransactionCostStrategy is an abstract base class that defines the interface
    for various transaction cost calculation strategies.
    """

    @abstractmethod
    def calculate(self, notional: Decimal, rate: Decimal) -> Decimal:
        """
        Calculates the transaction cost based on the given notional amount and rate.

        Parameters:
            notional (Decimal): The notional amount of the transaction.
            rate (Decimal): The rate used for cost calculation.

        Returns:
            Decimal: The calculated transaction cost.
        """
        pass


class GBCostStrategy(TransactionCostStrategy):
    """
    GBCostStrategy is implementation of TransactionCostStrategy
    used for calculating transaction costs in GB.
    """

    def calculate(self, notional: Decimal, rate: Decimal) -> Decimal:
        """
        Calculates the transaction cost for GB by multiplying notional with rate and then
        subtracting the notional.

        Parameters:
            notional (Decimal): The notional amount of the transaction.
            rate (Decimal): The rate used for cost calculation.

        Returns:
            Decimal: The calculated transaction cost in GB.
        """
        return notional * rate - notional


class NLCostStrategy(TransactionCostStrategy):
    """
    NLCostStrategy is implementation of TransactionCostStrategy
    used for calculating transaction costs in NL.
    """

    def calculate(self, notional: Decimal, rate: Decimal) -> Decimal:
        """
        Calculates the transaction cost for NL by taking the absolute value of
        (notional * (1 / rate) - notional).

        Parameters:
            notional (Decimal): The notional amount of the transaction.
            rate (Decimal): The rate used for cost calculation.

        Returns:
            Decimal: The calculated transaction cost in NL.
        """
        return abs(notional * (1 / rate) - notional)


country_strategies: Dict[str, TransactionCostStrategy] = {
    "GB": GBCostStrategy(),
    "NL": NLCostStrategy(),
}
