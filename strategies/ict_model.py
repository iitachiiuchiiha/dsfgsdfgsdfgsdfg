# File: 1_Strategies/ict_model.py
from .base_strategy import BaseStrategy
import pandas as pd

class ICTModel(BaseStrategy):
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        print(f"Applying strategy: {self.__class__.__name__}")
        
        # HNA FIN GHADI TKTEB L-QAWA3ID DYAL ICT
        # B7al Fair Value Gaps, Order Blocks, etc.
        
        data['signal'] = 0 # Bda b 0 (la signal)
        
        # Mital:
        # for i in range(1, len(data)):
        #     if condition_buy:
        #         data.loc[data.index[i], 'signal'] = 1 # Buy
        #     elif condition_sell:
        #         data.loc[data.index[i], 'signal'] = -1 # Sell
        
        return data