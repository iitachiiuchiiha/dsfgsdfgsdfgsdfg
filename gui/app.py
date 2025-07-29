from flask import Flask, render_template, Response
import json
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import sys
import os
import traceback
from pandas import Timestamp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_handler.data_fetcher import get_all_symbols, get_market_data, get_tick_data

app = Flask(__name__)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Timestamp): return obj.isoformat()
        if isinstance(obj, np.integer): return int(obj)
        elif isinstance(obj, np.floating): return float(obj)
        elif isinstance(obj, np.ndarray): return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

app.json_encoder = NumpyEncoder

TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
    "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4, "D1": mt5.TIMEFRAME_D1,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_symbols')
def api_get_symbols():
    symbols = get_all_symbols()
    return Response(json.dumps(symbols), mimetype='application/json')

@app.route('/api/get_chart/<symbol_name>/<timeframe_str>')
def api_get_chart(symbol_name, timeframe_str):
    try:
        timeframe = TIMEFRAME_MAP.get(timeframe_str, mt5.TIMEFRAME_H1)
        num_candles = 2000 if timeframe <= mt5.TIMEFRAME_M15 else 800
        
        df = get_market_data(symbol_name, timeframe, num_candles)
        if df is None or df.empty:
            return Response(json.dumps({"error": "No chart data available."}), mimetype='application/json')

        ohlcv = [
            {
                'time': int(row['time'].timestamp()), 'open': float(row['open']),
                'high': float(row['high']), 'low': float(row['low']),
                'close': float(row['close']), 'volume': float(row['tick_volume'])
            } for i, row in df.iterrows()
        ]
        return Response(json.dumps({'ohlcv': ohlcv}), mimetype='application/json')
    except Exception as e:
        print(f"!!! SERVER ERROR in /api/get_chart: {e} !!!\n{traceback.format_exc()}")
        return Response(json.dumps({"error": "Server Error"}), mimetype='application/json', status=500)

@app.route('/api/get_ticks/<symbol_name>')
def api_get_ticks(symbol_name):
    try:
        df_ticks = get_tick_data(symbol_name, num_ticks=1)
        if df_ticks is None or df_ticks.empty:
            return Response(json.dumps({}), mimetype='application/json')
        
        last_time = df_ticks['time'].iloc[-1]
        last_price = df_ticks['last_price'].iloc[-1]
        
        # Kansta3mlo l'wa9t dyal l'candle l'akhira bach l'update maykhserch l'chart
        tick_data = { 'time': int(last_time.timestamp()), 'price': float(last_price) }
        
        return Response(json.dumps(tick_data, cls=NumpyEncoder), mimetype='application/json')
    except Exception as e:
        # Hado machi erreurs khaybin, kan ignoriwhom bach may3emroch l'console
        # print(f"!!! SERVER ERROR in /api/get_ticks: {e} !!!")
        return Response(json.dumps({"error": "No new tick"}), mimetype='application/json', status=500)