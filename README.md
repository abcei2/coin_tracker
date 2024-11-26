# Coin Tracker

A Python application that tracks cryptocurrency prices using the Binance API, stores historical data in PostgreSQL, and provides price predictions using machine learning.

## Features

- Real-time cryptocurrency price tracking
- Historical data synchronization for multiple cryptocurrencies
- Price predictions using linear regression
- Error margin calculations for predictions
- PostgreSQL database integration using Peewee ORM
- Environment variable configuration
- Bulk data insertion for optimal performance

## Prerequisites

- Python 3.7+
- PostgreSQL
- Binance API credentials

## Installation

1. Clone the repository:

```bash
git clone 
```

## Technical Details

### Data Collection
- Fetches historical price data from Binance API
- Stores minute-by-minute price data
- Supports bulk synchronization of historical data

### Price Predictions
- Uses linear regression model for price predictions
- Analyzes 24 hours of historical data
- Provides predictions for next 10 minutes
- Includes error margin based on price volatility
- Stores predictions in separate database table

## Database Schema

### Tables
1. coin_prices
   - symbol: cryptocurrency pair
   - price: historical price point
   - timestamp: when price was recorded

2. price_predictions
   - symbol: cryptocurrency pair
   - predicted_price: forecasted price
   - error_margin: prediction uncertainty range
   - prediction_timestamp: when prediction was made
   - target_timestamp: prediction target time



