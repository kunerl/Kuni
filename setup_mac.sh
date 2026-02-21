#!/bin/bash
# ============================================
#  Stock Evaluator — Setup & Start
#  Zielordner: /Users/jan/Downloads/Aktien
# ============================================

set -e

TARGET="/Users/jan/Downloads/Aktien"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Stock Evaluator — Setup            ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Ordner erstellen falls nötig
mkdir -p "$TARGET"

# Projektdateien kopieren
echo "  Kopiere Dateien nach $TARGET ..."

# Quellverzeichnis = wo dieses Skript liegt
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Verzeichnisstruktur anlegen
mkdir -p "$TARGET/stock_evaluator/templates"
mkdir -p "$TARGET/stock_evaluator/static"
mkdir -p "$TARGET/tests"

# Dateien kopieren
cp "$SCRIPT_DIR/requirements.txt" "$TARGET/"
cp "$SCRIPT_DIR/run_web.py" "$TARGET/"
cp "$SCRIPT_DIR/stock_evaluator/"*.py "$TARGET/stock_evaluator/"
cp "$SCRIPT_DIR/stock_evaluator/templates/"*.html "$TARGET/stock_evaluator/templates/"
cp "$SCRIPT_DIR/stock_evaluator/static/"* "$TARGET/stock_evaluator/static/"
cp "$SCRIPT_DIR/tests/"*.py "$TARGET/tests/" 2>/dev/null || true

# start.command kopieren (falls vorhanden)
if [ -f "$SCRIPT_DIR/start.command" ]; then
    cp "$SCRIPT_DIR/start.command" "$TARGET/"
    chmod +x "$TARGET/start.command"
fi

echo "  Dateien kopiert."
echo ""

# Python venv erstellen
if [ ! -d "$TARGET/venv" ]; then
    echo "  Erstelle Python-Umgebung ..."
    python3 -m venv "$TARGET/venv"
    echo "  Python-Umgebung erstellt."
fi

# Dependencies installieren
echo "  Installiere Abhängigkeiten ..."
"$TARGET/venv/bin/pip" install --quiet --upgrade pip
"$TARGET/venv/bin/pip" install --quiet -r "$TARGET/requirements.txt"
echo "  Abhängigkeiten installiert."

echo ""
echo "  ✓ Setup abgeschlossen!"
echo "  Ordner: $TARGET"
echo ""
echo "  Zum Starten:"
echo "    Doppelklick auf: $TARGET/start.command"
echo "  Oder im Terminal:"
echo "    cd $TARGET && venv/bin/python run_web.py --public"
echo ""
