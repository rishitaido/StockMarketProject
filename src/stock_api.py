import requests 
import pandas as pd
import config
import os
import time
import json 
from datetime import datetime, timedelta 

CACHE_DIR = '/Users/rishi/StockMarketProject/data/cache'


def get_stock_price(symbol = config.DEFAULT_SYMBOL):
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': config.API_KEY
    }
    response = requests.get(config.BASE_URL, params=params)
    data=response.json() 

    if "Global Quote" not in data or data["Global Quote"] == {}:
        print("Debug Response:", data)
        raise ValueError(f"No data returned for symbol '{symbol}'.")

    return data['Global Quote']
    
def get_historical_data(symbol=config.DEFAULT_SYMBOL, interval=config.DEFAULT_INTERVAL, outputsize=config.DEFAULT_OUTPUTSIZE):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': interval,
        'outputsize': outputsize,
        'apikey': config.API_KEY
    }

    cache_file = f'{CACHE_DIR}{symbol}_{interval}.json'

    # Check cache
    if config.CACHE_ENABLED and os.path.exists(cache_file):
        cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if cache_age < timedelta(seconds=config.CACHE_EXPIRY):
            with open(cache_file, 'r') as f:
                print("Using cached data...")
                data = json.load(f)
                df = pd.DataFrame(data).T
                df.index = pd.to_datetime(df.index)
                return df.astype(float)

    response = requests.get(config.BASE_URL, params=params)
    data = response.json()

    # Dynamic key handling for safety
    time_series_key = next((key for key in data.keys() if 'Time Series' in key), None)

    if time_series_key:
        df = pd.DataFrame(data[time_series_key]).T
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)

        # Cache data
        if config.CACHE_ENABLED:
            with open(cache_file, 'w') as f:
                json.dump(data[time_series_key], f)

        return df
    else:
        # Print API response for debugging
        print("API Response:", data)
        raise ValueError(f"No historical data found for symbol '{symbol}'.")


# Test if module works directly
if __name__ == '__main__':
    print(get_stock_price())
    print(get_historical_data().head())

