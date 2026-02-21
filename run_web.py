"""Startet das Web-Interface des Stock Evaluators.

Verwendung:
    python run_web.py                  # Lokal (nur WLAN)
    python run_web.py --public         # Öffentlich (auch über mobile Daten)
    python run_web.py --public --port 8080
"""

import argparse
import sys
import threading


def start_tunnel(port: int) -> str:
    """Startet einen ngrok-Tunnel und gibt die öffentliche URL zurück."""
    try:
        from pyngrok import ngrok
    except ImportError:
        print("Fehler: pyngrok nicht installiert.")
        print("  pip install pyngrok")
        sys.exit(1)

    public_url = ngrok.connect(port, "http").public_url

    # HTTPS erzwingen
    if public_url.startswith("http://"):
        public_url = public_url.replace("http://", "https://", 1)

    return public_url


def main():
    parser = argparse.ArgumentParser(description="Stock Evaluator Web-Interface")
    parser.add_argument(
        "--public",
        action="store_true",
        help="Öffentlichen Tunnel starten (erreichbar über Internet/SIM)",
    )
    parser.add_argument("--port", type=int, default=5000, help="Port (Standard: 5000)")
    parser.add_argument("--no-debug", action="store_true", help="Debug-Modus deaktivieren")
    args = parser.parse_args()

    from stock_evaluator.web import run_server

    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║       STOCK EVALUATOR                ║")
    print("  ╚══════════════════════════════════════╝")
    print()

    if args.public:
        public_url = start_tunnel(args.port)
        print(f"  Öffentliche URL (funktioniert überall):")
        print(f"  → {public_url}")
        print()
        print("  Diese URL im iPhone-Browser öffnen")
        print("  oder QR-Code scannen auf: http://localhost:4040")
    else:
        print(f"  Lokal: http://localhost:{args.port}")
        print(f"  WLAN:  http://<DEINE-IP>:{args.port}")
        print()
        print("  Tipp: Mit --public auch über mobile Daten erreichbar")

    print()
    print("  Stoppen mit Ctrl+C")
    print()

    run_server(host="0.0.0.0", port=args.port, debug=not args.no_debug)


if __name__ == "__main__":
    main()
