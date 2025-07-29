# main.py

import sys
import os
import webview
import threading
from waitress import serve

# --- Configuration du chemin d'accès ---
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Importation de l'application Flask ---
# Toute la logique est maintenant dans gui/app.py
from gui.app import app

def run_server():
    """Démarre le serveur Flask en arrière-plan."""
    serve(app, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    # On lance le serveur Flask dans un thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # On crée la fenêtre de l'application desktop
    # NOTE: On n'utilise plus le paramètre js_api pour éviter les bugs
    webview.create_window(
        'Trading Bot Dashboard',
        'http://127.0.0.1:5000',
        width=1600,
        height=900,
        min_size=(1280, 800)
    )
    
    webview.start(debug=True)