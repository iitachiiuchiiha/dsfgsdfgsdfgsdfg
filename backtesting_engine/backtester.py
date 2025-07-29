# backtesting_engine/backtester.py (Version Mock)
import pandas as pd
import numpy as np
import time

class MockDataHandler:
    def __init__(self, chart_notifier=None):
        self.chart_notifier = chart_notifier # Pour envoyer les données au chart
        self.last_prices = {'EUR/USD': 1.0750, 'GBP/USD': 1.2550}
        self.history = {pair: [] for pair in self.last_prices.keys()}

    def get_latest_bars(self, symbol, timeframe, n_bars):
        # ... (même logique de génération de bougie)
        price = self.last_prices[symbol]
        open_price = price
        # ... etc
        close_price = np.random.uniform(low_price, high_price)
        self.last_prices[symbol] = close_price
        
        new_candle_data = {
            'time': pd.to_datetime('now', utc=True),
            'open': open_price, 'high': high_price,
            'low': low_price, 'close': close_price
        }
        self.history[symbol].append(new_candle_data)
        
        # === AJOUT IMPORTANT ===
        # Envoyer la nouvelle bougie à l'interface via le notificateur
        if self.chart_notifier:
            candle_for_chart = {
                'time': int(new_candle_data['time'].timestamp()), # Timestamp UNIX
                'open': new_candle_data['open'],
                'high': new_candle_data['high'],
                'low': new_candle_data['low'],
                'close': new_candle_data['close'],
            }
            self.chart_notifier(candle_for_chart)
        # =======================

        if len(self.history[symbol]) > n_bars + 5:
            self.history[symbol] = self.history[symbol][-n_bars:]

        df = pd.DataFrame(self.history[symbol])
        df.set_index('time', inplace=True)
        return df