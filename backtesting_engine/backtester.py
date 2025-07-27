# File: 3_Backtesting_Engine/backtester.py
import pandas as pd

class Backtester:
    def __init__(self, initial_capital=10000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position = 0
        self.trades = []

    def run(self, data_with_signals: pd.DataFrame):
        print("\n--- Starting Backtest ---")
        
        for i in range(len(data_with_signals)):
            signal = data_with_signals['signal'].iloc[i]
            price = data_with_signals['close'].iloc[i]
            
            # Ila kan signal BUY o ma3ndnach position
            if signal == 1 and self.position == 0:
                self.position = self.cash / price # Chri b ga3 l-cash
                print(f"{data_with_signals['time'].iloc[i]} | BUY at {price:.5f}")
                self.cash = 0

            # Ila kan signal SELL o 3ndna position
            elif signal == -1 and self.position > 0:
                self.cash = self.position * price
                print(f"{data_with_signals['time'].iloc[i]} | SELL at {price:.5f} | P/L: {(self.cash - self.initial_capital):.2f}")
                self.position = 0
        
        # Ila bqat position m7lola f lkher
        if self.position > 0:
            self.cash = self.position * data_with_signals['close'].iloc[-1]
            
        final_profit = self.cash - self.initial_capital
        final_return = (final_profit / self.initial_capital) * 100
        
        print("\n--- Backtest Finished ---")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Capital:   ${self.cash:,.2f}")
        print(f"Profit/Loss:     ${final_profit:,.2f}")
        print(f"Return:          {final_return:.2f}%")