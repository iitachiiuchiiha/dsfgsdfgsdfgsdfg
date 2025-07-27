import webview
from gui.app import app

if __name__ == '__main__':
    webview.create_window(
        'Advanced Trading System',
        app,
        width=1200,
        height=800,
        resizable=True,
        min_size=(900, 700)
    )
    webview.start(debug=True)