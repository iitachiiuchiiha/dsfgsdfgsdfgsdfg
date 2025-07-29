# gui/app.py

from flask import Flask, render_template, request, jsonify
from data_handler.mt5_data_handler import MT5DataHandler

# --- Initialisation ---
app = Flask(__name__)

# On crée une seule instance du DataHandler pour toute l'application
try:
    data_handler = MT5DataHandler()
except ConnectionError as e:
    print(f"ERREUR CRITIQUE: {e}")
    data_handler = None

# --- Route principale qui sert l'interface ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API Routes (appelées par JavaScript via fetch) ---

@app.route('/api/symbols')
def get_symbols():
    """Retourne la liste de tous les symboles disponibles depuis MT5."""
    if not data_handler:
        return jsonify({"error": "MT5 non connecté"}), 500
    
    symbols = data_handler.get_all_symbols()
    return jsonify(symbols)

@app.route('/api/historical_data')
def get_historical_data():
    """Retourne les données historiques pour un symbole et un timeframe donnés."""
    symbol = request.args.get('symbol')
    timeframe = request.args.get('timeframe')
    
    if not symbol or not timeframe:
        return jsonify({"error": "Symbole ou timeframe manquant"}), 400
        
    if not data_handler:
        return jsonify({"error": "MT5 non connecté"}), 500

    print(f"Flask: Récupération des données pour {symbol} ({timeframe})")
    data = data_handler.get_historical_bars(symbol, timeframe, 300) # On charge 300 bougies
    return jsonify(data)