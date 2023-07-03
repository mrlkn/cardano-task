from _decimal import Decimal
from pydantic import BaseModel
from typing import List

from app.enricher.cost_strategy_pattern import country_strategies


class LegalName(BaseModel):
    name: str
    language: str


class LegalAddress(BaseModel):
    addressLines: List[str]
    city: str
    country: str
    postalCode: str


class Entity(BaseModel):
    legalName: LegalName
    legalAddress: LegalAddress
    headquartersAddress: LegalAddress


class Registration(BaseModel):
    initialRegistrationDate: str
    lastUpdateDate: str
    status: str
    nextRenewalDate: str


class LeiRecordAttributes(BaseModel):
    lei: str
    entity: Entity
    registration: Registration
    bic: List[str]


class LeiRecord(BaseModel):
    type: str
    id: str
    attributes: LeiRecordAttributes
    transaction_cost: float = None

    def calculate_transaction_costs(self, notional: Decimal, rate: Decimal):
        country = self.attributes.entity.legalAddress.country
        strategy = country_strategies.get(country)

        if strategy:
            return strategy.calculate(notional, rate)
        else:
            raise ValueError(f"No strategy defined for country code: {country}")
