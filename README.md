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
- Implements unique identifier system for each price record
- Supports bulk synchronization of historical data

### Unique Identifier System
Each record uses a composite unique ID with format:
`{symbol}_{interval}_{timestamp_ms}`
Example: `BTCUSDT_1m_1683900000000`
- symbol: Trading pair (e.g., BTCUSDT)
- interval: Timeframe (e.g., 1m for one minute)
- timestamp_ms: Unix timestamp in milliseconds

### Price Predictions
The prediction system uses Linear Regression with the following approach:

1. Data Preparation:
   - Collects last 24 hours of price data
   - X-axis: Time in seconds from start
   - Y-axis: Actual prices

2. Model Training:
   - Fits a linear regression line through price points
   - Formula: P(t) = mt + b
     - P(t): Predicted price at time t
     - m: Price change rate
     - b: Base price level
     - t: Time in seconds from start

3. Prediction Generation:
   - Projects the line 10 minutes into future
   - Calculates error margin using standard deviation
   - Error margin reflects recent price volatility

4. Accuracy Metrics:
   - Error margin calculated from last 60 minutes
   - Wider margins indicate higher volatility
   - Predictions stored with timestamps for validation

## Database Schema

### Tables
1. coin_prices
   - unique_id: Composite identifier (primary key)
   - symbol: cryptocurrency pair
   - price: historical price point
   - interval: timeframe (e.g., 1m)
   - timestamp: when price was recorded

2. price_predictions
   - unique_id: Composite identifier (primary key)
   - symbol: cryptocurrency pair
   - predicted_price: forecasted price
   - error_margin: prediction uncertainty range
   - interval: timeframe (e.g., 1m)
   - prediction_timestamp: when prediction was made
   - target_timestamp: prediction target time



