#!/bin/bash
# ============================================
#  Stock Evaluator — Per Doppelklick starten
# ============================================

cd "$(dirname "$0")"

clear
echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║       STOCK EVALUATOR                ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Prüfe ob venv existiert
if [ ! -d "venv" ]; then
    echo "  Erstmalige Einrichtung läuft ..."
    echo ""
    python3 -m venv venv
    venv/bin/pip install --quiet --upgrade pip
    venv/bin/pip install --quiet -r requirements.txt
    echo "  Einrichtung abgeschlossen!"
    echo ""
fi

# Prüfe ob ngrok konfiguriert ist
if venv/bin/python -c "from pyngrok import ngrok; ngrok.get_tunnels()" 2>/dev/null; then
    echo "  Starte mit öffentlichem Zugang ..."
    echo "  (URL wird gleich angezeigt — am iPhone öffnen)"
    echo ""
    venv/bin/python run_web.py --public --no-debug
else
    echo "  Starte im lokalen Modus (nur WLAN) ..."
    echo ""
    echo "  Für Internet-Zugang (auch über SIM):"
    echo "    1. Gehe auf ngrok.com → kostenlosen Account erstellen"
    echo "    2. Auth-Token kopieren"
    echo "    3. Im Terminal ausführen:"
    echo "       $(pwd)/venv/bin/ngrok config add-authtoken DEIN_TOKEN"
    echo "    4. Danach nochmal doppelklicken"
    echo ""
    venv/bin/python run_web.py --no-debug
fi
