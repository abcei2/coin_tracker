from binance.client import Client
from models import db, CoinPrice, PricePrediction
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from datetime import datetime, timedelta
from peewee import IntegrityError, chunked
from typing import List
import numpy as np
from sklearn.linear_model import LinearRegression


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([CoinPrice], safe=True)
    db.close()


def get_coin_price(client, symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])


def get_historical_klines(client, symbol, start_date, end_date):
    klines = client.get_historical_klines(
        symbol,
        Client.KLINE_INTERVAL_1MINUTE,
        start_date.strftime("%d %b %Y %H:%M:%S"),
        end_date.strftime("%d %b %Y %H:%M:%S"),
    )
    return klines


def bulk_insert_prices(prices: List[dict]):
    with db.atomic():
        for batch in chunked(prices, 100):
            CoinPrice.insert_many(batch).on_conflict_ignore().execute()


def generate_unique_id(symbol: str, interval: str, timestamp: datetime) -> str:
    return f"{symbol}_{interval}_{int(timestamp.timestamp() * 1000)}"


def sync_historical_data(client, symbols, start_date, end_date):
    print(f"Starting fast sync from {start_date} to {end_date}")
    
    for symbol in symbols:
        klines = get_historical_klines(client, symbol, start_date, end_date)
        prices = [
            {
                'unique_id': generate_unique_id(symbol, '1m', datetime.fromtimestamp(kline[0] / 1000)),
                'symbol': symbol,
                'interval': '1m',
                'price': float(kline[4]),
                'timestamp': datetime.fromtimestamp(kline[0] / 1000)
            }
            for kline in klines
        ]
        
        bulk_insert_prices(prices)
        print(f"Synced {len(prices)} records for {symbol}")


def predict_price(symbol: str, prediction_minutes: int = 10):
    # Get the last 24 hours of data
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    historical_prices = (CoinPrice
                        .select()
                        .where(
                            (CoinPrice.symbol == symbol) &
                            (CoinPrice.timestamp.between(start_time, end_time))
                        )
                        .order_by(CoinPrice.timestamp)
                        .execute())
    
    if not historical_prices:
        return None

    # Prepare data for linear regression
    times = np.array([(p.timestamp - start_time).total_seconds() for p in historical_prices])
    prices = np.array([p.price for p in historical_prices])
    
    times = times.reshape(-1, 1)
    
    # Create and fit the model
    model = LinearRegression()
    model.fit(times, prices)
    
    # Calculate prediction time
    target_timestamp = end_time + timedelta(minutes=prediction_minutes)
    prediction_time = np.array([(target_timestamp - start_time).total_seconds()]).reshape(-1, 1)
    
    # Make prediction
    predicted_price = float(model.predict(prediction_time)[0])
    
    # Calculate error margin (using standard deviation of recent prices)
    error_margin = float(np.std(prices[-60:]) if len(prices) >= 60 else np.std(prices))
    
    prediction_timestamp = datetime.now()
    unique_id = generate_unique_id(symbol, '1m', target_timestamp)
    
    # Save prediction
    PricePrediction.create(
        unique_id=unique_id,
        symbol=symbol,
        predicted_price=predicted_price,
        error_margin=error_margin,
        interval='1m',
        target_timestamp=target_timestamp
    )
    
    return {
        'symbol': symbol,
        'predicted_price': predicted_price,
        'error_margin': error_margin,
        'target_timestamp': target_timestamp
    }


def main():
    # Initialize Binance client
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    coins = ["BTCUSDT", "SHIBUSDT"]
    
    # Initialize database
    init_db()
    db.create_tables([PricePrediction], safe=True)

    # Sync last 10 days of data
    end_date = datetime.now() + timedelta(hours=5) - timedelta(minutes=10)
    start_date = end_date - timedelta(days=10)
    
    sync_historical_data(client, coins, start_date, end_date)
    print("Historical data sync completed")
    
    # Generate predictions
    print("\nGenerating predictions:")
    for coin in coins:
        prediction = predict_price(coin)
        if prediction:
            print(f"{coin} prediction for {prediction['target_timestamp']}:")
            print(f"Price: {prediction['predicted_price']:.8f} ± {prediction['error_margin']:.8f}")


if __name__ == "__main__":
    main()
