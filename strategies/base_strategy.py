# File: 1_Strategies/base_strategy.py
import pandas as pd

class BaseStrategy:
    """
    Hadi hiya l-class l-asassiya l-ga3 les stratégies.
    Ay istratijia khassha twret men hna.
    """
    def __init__(self, params={}):
        self.params = params

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Hadi hiya l-function l-ra2issiya li khass ay istratijia t3emmerha.
        Katched data o katkhrej les signaux dyal chra/bi3.
        """
        print(f"Applying strategy: {self.__class__.__name__}")
        # Hada khasso ytrje3 nafs l-DataFrame m3a des colonnes jdad 'signal'
        # 'signal' yqdr ykon 1 (Buy), -1 (Sell), 0 (Do Nothing)
        data['signal'] = 0 
        return data