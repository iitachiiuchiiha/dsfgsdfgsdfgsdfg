import MetaTrader5 as mt5
import pandas as pd

def get_market_data(symbol, timeframe, num_candles):
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

def get_all_symbols():
    if not mt5.initialize():
        return []
    
    symbols = mt5.symbols_get()
    mt5.shutdown()
    
    if symbols is None: return []
    return [s.name for s in symbols]