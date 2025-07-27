from flask import Flask, render_template, Response
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import json
import sys
import os
import traceback
from pandas import Timestamp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_handler.data_fetcher import get_all_symbols, get_market_data

app = Flask(__name__)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Timestamp): return obj.isoformat()
        if isinstance(obj, np.integer): return int(obj)
        elif isinstance(obj, np.floating): return float(obj)
        elif isinstance(obj, np.ndarray): return obj.tolist()
        return json.JSONEncoder.default(self, obj)

TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
    "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4, "D1": mt5.TIMEFRAME_D1,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_symbols')
def api_get_symbols():
    return Response(json.dumps(get_all_symbols()), mimetype='application/json')

@app.route('/api/get_chart/<symbol_name>/<timeframe_str>')
def api_get_chart(symbol_name, timeframe_str):
    try:
        timeframe = TIMEFRAME_MAP.get(timeframe_str, mt5.TIMEFRAME_H1)
        num_candles = 2000 if timeframe <= mt5.TIMEFRAME_M15 else 800
        
        df = get_market_data(symbol_name, timeframe, num_candles)
        if df is None or df.empty:
            return Response(json.dumps({"error": "No chart data available."}), mimetype='application/json')

        # Prepare OHLCV data for Lightweight Charts
        ohlcv = []
        for i, row in df.iterrows():
            ohlcv.append({
                'time': int(row['time'].timestamp()),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['tick_volume'])
            })
        json_response = json.dumps({'ohlcv': ohlcv})
        return Response(json_response, mimetype='application/json')

    except Exception as e:
        print(f"!!! SERVER ERROR: {e} !!!")
        print(traceback.format_exc())
        return Response(json.dumps({"error": f"Server Error: Check terminal for details."}), mimetype='application/json')