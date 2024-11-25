from peewee import *
from datetime import datetime
from config import DB_CONFIG

db = PostgresqlDatabase(**DB_CONFIG)

class BaseModel(Model):
    class Meta:
        database = db

class CoinPrice(BaseModel):
    symbol = CharField()
    price = FloatField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'coin_prices'
        indexes = (
            (('symbol', 'timestamp'), True),  # Unique index
        )