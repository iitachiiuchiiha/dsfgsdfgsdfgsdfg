# data_handler/mt5_data_handler.py
import MetaTrader5 as mt5
import pandas as pd

class MT5DataHandler:
    def __init__(self):
        if not self._connect():
            raise ConnectionError("Impossible de se connecter à MetaTrader 5. Veuillez vérifier que la plateforme est lancée et que l'Algo Trading est activé.")

    def _connect(self):
        if not mt5.initialize():
            print(f"initialize() a échoué, code d'erreur = {mt5.last_error()}")
            return False
        print("Connexion à MetaTrader5 réussie.")
        return True
    
    def get_all_symbols(self):
        try:
            symbols = mt5.symbols_get()
            if symbols:
                return sorted([s.name for s in symbols])
            return []
        except Exception as e:
            print(f"Erreur lors de la récupération des symboles: {e}")
            return []

    def get_historical_bars(self, symbol, timeframe_str, n_bars):
        try:
            rates = mt5.copy_rates_from_pos(symbol, self._get_mt5_timeframe(timeframe_str), 0, n_bars)
            if rates is None or len(rates) == 0:
                print(f"Aucune donnée historique trouvée pour {symbol}")
                return []
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            return [{
                'time': int(row['time'].timestamp()),
                'open': row['open'], 'high': row['high'],
                'low': row['low'], 'close': row['close'],
            } for _, row in df.iterrows()]
        except Exception as e:
            print(f"Erreur lors de la récupération des barres historiques pour {symbol}: {e}")
            return []

    def _get_mt5_timeframe(self, tf_str):
        timeframes = {
            "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1, "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1,
        }
        return timeframes.get(tf_str.upper(), mt5.TIMEFRAME_H1)