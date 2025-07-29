# data_handler/mt5_data_handler.py

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz

class MT5DataHandler:
    """
    Ce DataHandler se connecte à MetaTrader 5 pour obtenir les données du marché en temps réel.
    """
    def __init__(self, chart_notifier=None, log_notifier=None):
        self.chart_notifier = chart_notifier
        # Si log_notifier n'est pas fourni, on utilise print() par défaut
        self.log = log_notifier if log_notifier else print
        
        if not self._connect():
            raise ConnectionError("Failed to connect to MetaTrader 5")

    def _connect(self):
        """Initialise la connexion à la plateforme MetaTrader 5."""
        if not mt5.initialize():
            self.log(f"initialize() failed, error code = {mt5.last_error()}", level="error")
            return False
        self.log("MetaTrader5 connection successful.", level="info")
        return True

    def get_latest_bars(self, symbol, timeframe_str, n_bars):
        """
        Récupère les N dernières bougies pour un symbole donné.
        Cette fonction est appelée en boucle par le bot.
        """
        try:
            rates = mt5.copy_rates_from_pos(symbol, self._get_mt5_timeframe(timeframe_str), 0, n_bars)
            if rates is None or len(rates) == 0:
                self.log(f"No rates returned for {symbol} from MT5.", level="warning")
                return None

            df = pd.DataFrame(rates)
            # Convertir le temps (timestamp) en objet datetime
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)

            # Envoyer la dernière bougie au chart pour la mise à jour en temps réel
            if self.chart_notifier and not df.empty:
                latest_candle = df.iloc[-1]
                candle_for_chart = {
                    'time': int(latest_candle.name.timestamp()),
                    'open': latest_candle['open'],
                    'high': latest_candle['high'],
                    'low': latest_candle['low'],
                    'close': latest_candle['close'],
                }
                self.chart_notifier(candle_for_chart)

            return df

        except Exception as e:
            self.log(f"Error getting latest bars for {symbol}: {e}", level="error")
            return None

    def get_historical_bars(self, symbol, timeframe_str, n_bars):
        """
        Récupère un bloc de données historiques pour initialiser le chart au démarrage.
        """
        try:
            rates = mt5.copy_rates_from_pos(symbol, self._get_mt5_timeframe(timeframe_str), 0, n_bars)
            if rates is None or len(rates) == 0:
                self.log(f"No historical rates returned for {symbol}", level="warning")
                return []

            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Formater les données pour lightweight-charts
            chart_data = [
                {
                    'time': int(row['time'].timestamp()),
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                } for index, row in df.iterrows()
            ]
            return chart_data

        except Exception as e:
            self.log(f"Error getting historical bars for {symbol}: {e}", level="error")
            return []

    def _get_mt5_timeframe(self, tf_str):
        """Convertit une chaîne de caractères (ex: "M1") en constante MT5."""
        timeframes = {
            "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1, "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1,
        }
        return timeframes.get(tf_str.upper(), mt5.TIMEFRAME_M1)

    def shutdown(self):
        """Ferme la connexion à MetaTrader 5."""
        mt5.shutdown()
        self.log("MetaTrader5 connection shut down.", level="info")