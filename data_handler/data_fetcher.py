import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

def get_all_symbols():
    """
    Katjib la liste kamla dyal les symboles men MetaTrader 5.
    """
    if not mt5.initialize():
        print("[FETCHER] ERROR: mt5.initialize() failed")
        return []
    
    symbols = mt5.symbols_get()
    mt5.shutdown()
    
    if symbols is None:
        print("[FETCHER] Ma l9ina ta symboles.")
        return []
    
    return [s.name for s in symbols]

def get_market_data(symbol, timeframe, num_candles):
    """
    Katjib data dyal chmou3 (candles) l'wa7ed l'symbol.
    """
    if not mt5.initialize():
        print("[FETCHER] ERROR: mt5.initialize() failed")
        return None
    
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
    mt5.shutdown()
    
    if rates is None or len(rates) == 0:
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def get_tick_data(symbol, num_ticks=1):
    """
    Katjib akher tick data (live price) l wa7ed l'symbol.
    """
    if not mt5.initialize():
        print("[TICK FETCHER] ERROR: mt5.initialize() failed")
        return None
    
    ticks = mt5.copy_ticks_from(symbol, datetime.now(), num_ticks, mt5.COPY_TICKS_ALL)
    mt5.shutdown()
    
    if ticks is None or len(ticks) == 0:
        return None

    df = pd.DataFrame(ticks)
    df['time_msc'] = pd.to_datetime(df['time_msc'], unit='ms')
    df.rename(columns={'time_msc': 'time', 'last': 'last_price'}, inplace=True)
    
    return df