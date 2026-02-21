"""Startet das Web-Interface des Stock Evaluators."""

from stock_evaluator.web import run_server

if __name__ == "__main__":
    print("Stock Evaluator Web-Interface")
    print("Öffne im iPhone-Browser: http://<DEINE-IP>:5000")
    print("Stoppen mit Ctrl+C")
    run_server(host="0.0.0.0", port=5000, debug=True)
