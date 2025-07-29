# gui/app.py

import time
from flask import Flask, render_template
from threading import Thread, Event

# --- Importation des composants du bot ---
from backtesting_engine.backtester import MockDataHandler
from strategies.Forex_Price_Action_Scalping import ForexPriceActionScalping
from risk_management.risk_manager import MockRiskManager

# --- Initialisation de l'application Flask ---
app = Flask(__name__)

# --- Définition du Thread du Bot ---
bot_thread = None
thread_stop_event = Event()

class BotThread(Thread):
    def __init__(self, api_instance):
        self.api = api_instance
        super(BotThread, self).__init__()

    def run(self):
        """La boucle principale du bot."""
        self.api.log_to_gui("Bot thread started. Initializing components...")
        
        data_handler = MockDataHandler(chart_notifier=self.api.send_chart_data)
        risk_manager = MockRiskManager()
        strategy = ForexPriceActionScalping(
            data_handler=data_handler,
            risk_manager=risk_manager,
            gui_notifier=self.api.log_to_gui,
            trade_notifier=self.api.send_trade_signal
        )
        
        self.api.log_to_gui("Bot is running. Waiting for trading signals...")
        while not thread_stop_event.is_set():
            try:
                for pair in strategy.pairs:
                    strategy.check_signal(pair)
                time.sleep(1)
            except Exception as e:
                self.api.log_to_gui(f"An error occurred in bot loop: {e}", level="error")
                time.sleep(5)
        self.api.log_to_gui("Bot thread has been stopped.", level="warning")

# === CORRECTION IMPORTANTE ===
# La fonction doit accepter deux arguments: flask_app et api_instance
def start_bot_thread(flask_app, api_instance):
    """
    Fonction pour démarrer le bot. Elle accepte maintenant l'app Flask et l'API
    comme arguments pour éviter le problème de 'context'.
    """
    global bot_thread
    
    # On utilise le contexte de l'application pour s'assurer que tout fonctionne correctement
    with flask_app.app_context():
        if bot_thread is None or not bot_thread.is_alive():
            print("Starting Bot Thread...")
            thread_stop_event.clear()
            # On passe l'instance de l'API directement au constructeur du thread
            bot_thread = BotThread(api_instance=api_instance)
            bot_thread.daemon = True
            bot_thread.start()

# --- Définition des Routes Flask ---
@app.route('/')
def index():
    """Sert la page principale (index.html)."""
    return render_template('index.html')