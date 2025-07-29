# main.py
import sys, os, webview, threading
from waitress import serve
from gui.app import app, start_bot_thread

# Configuration du chemin
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
            self.window.evaluate_js(f'window.addTradeSignal({json.dumps(trade_data)})')
            
    def send_chart_data(self, chart_data):
        if self.window:
            import json
            self.window.evaluate_js(f'window.updateChart({json.dumps(chart_data)})')

    def send_historical_data(self, symbol, data):
        """Fonction pour envoyer le bloc de données historiques au JS."""
        if self.window:
            import json
            self.window.evaluate_js(f'window.loadHistoricalData({json.dumps(data)})')

api = Api()

def run_server():
    serve(app, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    print("Flask server started at http://127.0.0.1:5000")

    window = webview.create_window('Trading Bot Dashboard', 'http://127.0.0.1:5000', width=1600, height=900)
    api.window = window
    start_bot_thread(app, api)
    webview.start(debug=True)
    print("Desktop application closed.")