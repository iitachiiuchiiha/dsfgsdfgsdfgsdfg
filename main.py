import sys
import os
import webview
import threading
from waitress import serve

# === ÉTAPE 1: Configuration du chemin d'accès ===
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# === ÉTAPE 2: Importation des composants nécessaires ===
from gui.app import app, start_bot_thread

# === ÉTAPE 3: Création de l'API Bridge ===
class Api:
    def __init__(self):
        self.window = None

    def log_to_gui(self, message, level='info'):
        if self.window:
            safe_message = message.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
            self.window.evaluate_js(f'window.addLogMessage("{safe_message}", "{level}")')

    def send_trade_signal(self, trade_data):
        if self.window:
            import json
            trade_json = json.dumps(trade_data)
            self.window.evaluate_js(f'window.addTradeSignal({trade_json})')
            
    def send_chart_data(self, chart_data):
        if self.window:
            import json
            chart_json = json.dumps(chart_data)
            self.window.evaluate_js(f'window.updateChart({chart_json})')

api = Api()

# === ÉTAPE 4: Fonction pour lancer le serveur Flask ===
def run_server():
    """Démarre le serveur Flask en arrière-plan."""
    serve(app, host='127.0.0.1', port=5000)

# === ÉTAPE 5: Point d'entrée principal de l'application ===
if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    print("Flask server started in a background thread at http://127.0.0.1:5000")

    window = webview.create_window(
        'Trading Bot Dashboard',
        'http://127.0.0.1:5000',
        width=1600,
        height=900,
        resizable=True,
        min_size=(1024, 768)
    )
    
    api.window = window
    
    # === CORRECTION IMPORTANTE ===
    # On passe l'application Flask (app) et l'objet API (api) directement
    # à la fonction qui va démarrer le bot.
    start_bot_thread(app, api)
    
    webview.start(debug=True)
    
    print("Desktop application closed.")