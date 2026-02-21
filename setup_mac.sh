#!/bin/bash
# ============================================
#  Stock Evaluator — Komplettes Setup
#  Kopiere dieses Skript nach /Users/jan/Downloads/
#  und führe es aus: bash setup_mac.sh
# ============================================

set -e

TARGET="/Users/jan/Downloads/Aktien"
REPO="https://github.com/kunerl/Kuni.git"
BRANCH="claude/trading-stock-evaluation-tool-XM2Oh"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Stock Evaluator — Setup            ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# ----- 1. Prüfe ob python3 vorhanden -----
if ! command -v python3 &> /dev/null; then
    echo "  Fehler: python3 nicht gefunden."
    echo "  Bitte installiere Python 3:"
    echo "    https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo "  Python gefunden: $(python3 --version)"

# ----- 2. Prüfe ob git vorhanden -----
if ! command -v git &> /dev/null; then
    echo "  Fehler: git nicht gefunden."
    echo "  Installiere Xcode Command Line Tools:"
    echo "    xcode-select --install"
    echo ""
    exit 1
fi

# ----- 3. Repo klonen oder aktualisieren -----
if [ -d "$TARGET/.git" ]; then
    echo "  Aktualisiere bestehendes Projekt ..."
    cd "$TARGET"
    git pull origin "$BRANCH" 2>/dev/null || true
else
    echo "  Lade Projekt herunter ..."
    rm -rf "$TARGET"
    git clone --branch "$BRANCH" "$REPO" "$TARGET"
fi

cd "$TARGET"
echo "  Projekt geladen."
echo ""

# ----- 4. Python venv erstellen -----
if [ ! -d "$TARGET/venv" ]; then
    echo "  Erstelle Python-Umgebung ..."
    python3 -m venv "$TARGET/venv"
fi

# ----- 5. Dependencies installieren -----
echo "  Installiere Abhängigkeiten ..."
"$TARGET/venv/bin/pip" install --quiet --upgrade pip
"$TARGET/venv/bin/pip" install --quiet -r "$TARGET/requirements.txt"
echo "  Abhängigkeiten installiert."

# ----- 6. Icons generieren -----
echo "  Generiere App-Icons ..."
"$TARGET/venv/bin/python" -m stock_evaluator.generate_icons 2>/dev/null || true

# ----- 7. start.command ausführbar machen -----
chmod +x "$TARGET/start.command"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   ✓ Setup abgeschlossen!             ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  App starten:"
echo "    → Doppelklick auf: Downloads/Aktien/start.command"
echo ""
echo "  Oder im Terminal:"
echo "    cd $TARGET && venv/bin/python run_web.py --public"
echo ""
