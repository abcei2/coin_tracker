from binance.client import Client
from models import db, CoinPrice
import time
from config import BINANCE_API_KEY, BINANCE_API_SECRET

def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([CoinPrice], safe=True)
    db.close()

def get_coin_price(client, symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def main():
    # Initialize Binance client
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    
    # List of coins to track
    coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    # Initialize database
    init_db()
    
    try:
        while True:
            for symbol in coins:
                price = get_coin_price(client, symbol)
                
                # Save to database
                with db.atomic():
                    CoinPrice.create(
                        symbol=symbol,
                        price=price
                    )
                
                print(f"{symbol}: ${price}")
            
            # Wait for 1 minute before next update
            time.sleep(60)
    
    except KeyboardInterrupt:
        print("\nStopping coin tracker...")

if __name__ == "__main__":
    main()