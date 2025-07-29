# strategies/Forex_Price_Action_Scalping.py

import pandas as pd
from scipy.signal import find_peaks

class ForexPriceActionScalping:
    """
    Stratégie de scalping modifiée pour envoyer des notifications au GUI.
    """
    def __init__(self, data_handler, risk_manager, gui_notifier, trade_notifier):
        self.name = "Forex Price Action Scalping"
        self.data_handler = data_handler
        self.risk_manager = risk_manager
        
        # Fonctions de notification passées depuis app.py
        self.log = gui_notifier
        self.notify_trade = trade_notifier
        
        # Paramètres de la stratégie (depuis le PDF)
        self.pairs = ['EUR/USD', 'GBP/USD']
        self.timeframe = "M1"
        self.ema_period = 50
        self.min_profit_target_pips = 15.0
        self.max_stop_loss_pips = 15.0
        self.peak_detection_distance = 10
        self.trendline_lookback_period = 45

    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['ema_50'] = df['close'].ewm(span=self.ema_period, adjust=False).mean()
        df['ema_slope'] = df['ema_50'].diff()
        return df

    def _find_trendline_breakout(self, data: pd.DataFrame, is_uptrend: bool):
        if len(data) < self.trendline_lookback_period:
            return None, None

        current_candle = data.iloc[-1]
        previous_candles = data.iloc[-self.trendline_lookback_period:-1]

        try:
            if is_uptrend:
                highs_indices, _ = find_peaks(previous_candles['high'], distance=self.peak_detection_distance)
                if len(highs_indices) < 2: return None, None
                
                p1_idx, p2_idx = highs_indices[-2], highs_indices[-1]
                p1_time = previous_candles.index[p1_idx]
                p2_time = previous_candles.index[p2_idx]
                p1_price = previous_candles['high'].iloc[p1_idx]
                p2_price = previous_candles['high'].iloc[p2_idx]

                if p2_price >= p1_price: return None, None
                
                slope = (p2_price - p1_price) / ((p2_time - p1_time).total_seconds())
                trendline_value_now = p1_price + slope * ((current_candle.name - p1_time).total_seconds())

                if current_candle['close'] > trendline_value_now and current_candle['open'] <= trendline_value_now:
                    trendline_info = {
                        'p1': {'time': p1_time.isoformat(), 'price': p1_price},
                        'p2': {'time': p2_time.isoformat(), 'price': p2_price}
                    }
                    return 'BUY', trendline_info
            else: # is_downtrend
                lows_indices, _ = find_peaks(-previous_candles['low'], distance=self.peak_detection_distance)
                if len(lows_indices) < 2: return None, None
                
                p1_idx, p2_idx = lows_indices[-2], lows_indices[-1]
                p1_time = previous_candles.index[p1_idx]
                p2_time = previous_candles.index[p2_idx]
                p1_price = previous_candles['low'].iloc[p1_idx]
                p2_price = previous_candles['low'].iloc[p2_idx]
                
                if p2_price <= p1_price: return None, None

                slope = (p2_price - p1_price) / ((p2_time - p1_time).total_seconds())
                trendline_value_now = p1_price + slope * ((current_candle.name - p1_time).total_seconds())

                if current_candle['close'] < trendline_value_now and current_candle['open'] >= trendline_value_now:
                    trendline_info = {
                        'p1': {'time': p1_time.isoformat(), 'price': p1_price},
                        'p2': {'time': p2_time.isoformat(), 'price': p2_price}
                    }
                    return 'SELL', trendline_info
        except Exception as e:
            self.log(f"Error in trendline detection: {e}", level='error')

        return None, None

    def check_signal(self, symbol: str):
        try:
            data = self.data_handler.get_latest_bars(symbol, self.timeframe, 150)
            if data is None or data.empty:
                # self.log(f"No data received for {symbol}", level='warning')
                return
        except Exception as e:
            self.log(f"Error getting data for {symbol}: {e}", level='error')
            return

        df = self._calculate_indicators(data)
        latest_candle = df.iloc[-1]
        
        is_ema_sloping_up = latest_candle['ema_slope'] > 0
        is_price_above_ema = latest_candle['close'] > latest_candle['ema_50']
        is_ema_sloping_down = latest_candle['ema_slope'] < 0
        is_price_below_ema = latest_candle['close'] < latest_candle['ema_50']

        signal, trendline_info = None, None
        
        if is_ema_sloping_up and is_price_above_ema:
            signal, trendline_info = self._find_trendline_breakout(df, is_uptrend=True)
        elif is_ema_sloping_down and is_price_below_ema:
            signal, trendline_info = self._find_trendline_breakout(df, is_uptrend=False)

        if signal:
            self.execute_trade(signal, symbol, df.iloc[-2], trendline_info)

    def execute_trade(self, signal: str, symbol: str, breakout_candle: pd.Series, trendline_info: dict):
        pip_value = 0.0001 if "JPY" not in symbol else 0.01
        entry_price = breakout_candle['close']
        
        if signal == 'BUY':
            stop_loss_price = breakout_candle['low'] - (1 * pip_value)
            sl_pips = (entry_price - stop_loss_price) / pip_value
            if sl_pips > self.max_stop_loss_pips:
                self.log(f"BUY signal for {symbol} ignored. SL too large: {sl_pips:.1f} pips.", level='warning')
                return
            take_profit_price = entry_price + (self.min_profit_target_pips * pip_value)
        elif signal == 'SELL':
            stop_loss_price = breakout_candle['high'] + (1 * pip_value)
            sl_pips = (stop_loss_price - entry_price) / pip_value
            if sl_pips > self.max_stop_loss_pips:
                self.log(f"SELL signal for {symbol} ignored. SL too large: {sl_pips:.1f} pips.", level='warning')
                return
            take_profit_price = entry_price - (self.min_profit_target_pips * pip_value)
        else:
            return

        lot_size = self.risk_manager.calculate_lot_size(symbol, stop_loss_price)
        
        trade_data = {
            'type': 'trade_signal',
            'symbol': symbol,
            'signal': signal,
            'entry_price': round(entry_price, 5),
            'stop_loss': round(stop_loss_price, 5),
            'take_profit': round(take_profit_price, 5),
            'sl_pips': round(sl_pips, 1),
            'tp_pips': self.min_profit_target_pips,
            'risk_reward': round(self.min_profit_target_pips / sl_pips if sl_pips > 0 else 0, 2),
            'trendline': trendline_info,
            'breakout_candle_time': breakout_candle.name.isoformat()
        }
        
        self.log(f"Found {signal} signal for {symbol} at {entry_price:.5f}", level="signal")
        self.notify_trade(trade_data)
