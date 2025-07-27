# File: 1_Strategies/elliott_waves.py
from .base_strategy import BaseStrategy
import pandas as pd

class ElliottWaves(BaseStrategy):
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        print(f"Applying strategy: {self.__class__.__name__}")
        
        # HNA FIN GHADI TKTEB L-QAWA3ID DYAL ELLIOTT WAVES
        
        data['signal'] = 0
        return data