from app.settings.database import db
from peewee import Model, CharField, DecimalField, DateTimeField, DateField


class Transaction(Model):
    csv_last_modified_date = DateField()
    transaction_uti = CharField(max_length=100)
    isin = CharField(max_length=12)
    notional = DecimalField(max_digits=20, decimal_places=5)
    notional_currency = CharField(max_length=3)
    transaction_type = CharField(max_length=10)
    transaction_datetime = DateTimeField()
    rate = DecimalField(max_digits=10, decimal_places=7)
    lei = CharField(max_length=20)

    class Meta:
        database = db


db.connect()  # TODO: Have a proper migration handling script but for now I guess it's ok
db.create_tables([Transaction])
