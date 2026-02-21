# Stock Evaluator - Aktien-Bewertungstool

Ein Python-Tool zur Bewertung von Aktien für Kauf- und Verkaufsentscheidungen. Kombiniert **technische Analyse** und **Fundamentalanalyse** zu einer Gesamtempfehlung.

## Features

### Technische Analyse
- **RSI** (Relative Strength Index) - Überkauft/Überverkauft-Erkennung
- **MACD** (Moving Average Convergence Divergence) - Trendrichtung
- **SMA 50/200** - Golden Cross / Death Cross Erkennung
- **Bollinger Bänder** - Volatilitäts- und Preisextrem-Analyse
- **Volumen-Trend** - Handelsaktivitäts-Analyse

### Fundamentalanalyse
- **Bewertungskennzahlen**: KGV, KBV, KUV, PEG Ratio
- **Rentabilität**: Gewinnmarge, Eigenkapitalrendite (ROE), Gesamtkapitalrendite (ROA)
- **Dividende**: Dividendenrendite, Ausschüttungsquote
- **Wachstum**: Umsatz- und Gewinnwachstum
- **Verschuldung**: Verschuldungsgrad, Liquiditätsgrad
- **Analysten**: Kursziel und Empfehlungen

### Bewertungssystem
| Score | Signal |
|-------|--------|
| +50 bis +100 | STARKER KAUF |
| +20 bis +49 | KAUF |
| -20 bis +19 | HALTEN |
| -49 bis -21 | VERKAUF |
| -100 bis -50 | STARKER VERKAUF |

## Installation

```bash
pip install -r requirements.txt
```

## Verwendung

```bash
# Einzelne Aktie bewerten
python -m stock_evaluator AAPL

# Mehrere Aktien bewerten
python -m stock_evaluator AAPL MSFT GOOGL

# Deutsche Aktie mit 2 Jahren Historie
python -m stock_evaluator SAP.DE -p 2y

# Mehr Gewicht auf technische Analyse
python -m stock_evaluator TSLA --tw 0.6 --fw 0.4
```

## Tests

```bash
pip install pytest
pytest tests/
```

## Hinweis

Dieses Tool dient nur zu Informationszwecken und stellt keine Anlageberatung dar.
