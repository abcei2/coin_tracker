from binance.client import Client
from models import db, CoinPrice
import time
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from datetime import datetime, timedelta
from peewee import IntegrityError


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


def sync_historical_data(client, symbols, start_date, end_date):
    print(f"Syncing data from {start_date} to {end_date}")

    for symbol in symbols:
        klines = get_historical_klines(client, symbol, start_date, end_date)

        with db.atomic():
            for kline in klines:
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                try:
                    CoinPrice.create(
                        symbol=symbol,
                        price=float(kline[4]),  # Using closing price
                        timestamp=timestamp,
                    )
                except IntegrityError:
                    # Skip if record already exists
                    continue

        print(f"Synced {symbol} data for {len(klines)} minutes")


def main():
    # Initialize Binance client
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

    # List of coins to track
    coins = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

    # Initialize database
    init_db()

    # Example: Sync last 24 hours of historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    sync_historical_data(client, coins, start_date, end_date)

    try:
        while True:
            for symbol in coins:
                price = get_coin_price(client, symbol)

                # Save to database
                with db.atomic():
                    CoinPrice.create(symbol=symbol, price=price)

                print(f"{symbol}: ${price}")

            # Wait for 1 minute before next update
            time.sleep(60)

    except KeyboardInterrupt:
        print("\nStopping coin tracker...")


if __name__ == "__main__":
    main()
