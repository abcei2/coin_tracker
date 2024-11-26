from peewee import *
from datetime import datetime
from config import DB_CONFIG

db = PostgresqlDatabase(**DB_CONFIG)

class BaseModel(Model):
    class Meta:
        database = db

class CoinPrice(BaseModel):
    unique_id = CharField(primary_key=True)  # New primary key
    symbol = CharField()
    price = FloatField()
    interval = CharField(default='1m')  # Added interval field
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'coin_prices'
        indexes = (
            (('symbol', 'timestamp'), True),  # Unique index
        )

class PricePrediction(BaseModel):
    unique_id = CharField(primary_key=True)  # New primary key
    symbol = CharField()
    predicted_price = FloatField()
    error_margin = FloatField()
    interval = CharField(default='1m')  # Added interval field
    prediction_timestamp = DateTimeField(default=datetime.now)
    target_timestamp = DateTimeField()

    class Meta:
        table_name = 'price_predictions'
        indexes = (
            (('symbol', 'target_timestamp'), True),
        )