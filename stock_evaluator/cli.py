"""Kommandozeilen-Interface für das Aktien-Bewertungstool."""

import argparse
import sys

from .evaluator import evaluate_stock


def main() -> None:
    """Haupteinstiegspunkt für das CLI."""
    parser = argparse.ArgumentParser(
        description="Aktien-Bewertungstool: Bewertet Aktien für Kauf- und Verkaufsentscheidungen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Beispiele:\n"
            "  python -m stock_evaluator AAPL          # Apple bewerten\n"
            "  python -m stock_evaluator MSFT GOOGL    # Mehrere Aktien bewerten\n"
            "  python -m stock_evaluator SAP.DE -p 2y  # SAP (Frankfurt) mit 2 Jahren Historie\n"
            "  python -m stock_evaluator TSLA --tw 0.6 --fw 0.4  # Mehr Gewicht auf Technik\n"
        ),
    )
    parser.add_argument(
        "tickers",
        nargs="+",
        help="Börsenkürzel der zu bewertenden Aktien (z.B. AAPL, MSFT, SAP.DE)",
    )
    parser.add_argument(
        "-p", "--period",
        default="1y",
        choices=["3mo", "6mo", "1y", "2y", "5y"],
        help="Zeitraum für historische Daten (Standard: 1y)",
    )
    parser.add_argument(
        "--tw", "--technical-weight",
        type=float,
        default=0.4,
        dest="technical_weight",
        help="Gewichtung der technischen Analyse 0-1 (Standard: 0.4)",
    )
    parser.add_argument(
        "--fw", "--fundamental-weight",
        type=float,
        default=0.6,
        dest="fundamental_weight",
        help="Gewichtung der Fundamentalanalyse 0-1 (Standard: 0.6)",
    )

    args = parser.parse_args()

    for ticker in args.tickers:
        try:
            result = evaluate_stock(
                ticker=ticker,
                period=args.period,
                technical_weight=args.technical_weight,
                fundamental_weight=args.fundamental_weight,
            )
            print(result.summary)
            print()
        except ValueError as e:
            print(f"FEHLER bei {ticker}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Unerwarteter Fehler bei {ticker}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
