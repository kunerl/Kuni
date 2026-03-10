"""Web-Interface für das Aktien-Bewertungstool."""

from pathlib import Path

from flask import Flask, render_template, request

from .evaluator import evaluate_stock
from .sharepoint import SharePointClient, SharePointConfig, get_demo_report

_pkg_dir = Path(__file__).parent
app = Flask(
    __name__,
    template_folder=str(_pkg_dir / "templates"),
    static_folder=str(_pkg_dir / "static"),
    static_url_path="/static",
)


@app.route("/")
def index():
    """Startseite mit Eingabeformular."""
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """Bewertet eine Aktie und gibt das Ergebnis zurück."""
    ticker = request.form.get("ticker", "").strip().upper()
    period = request.form.get("period", "1y")

    if not ticker:
        return render_template("index.html", error="Bitte ein Börsenkürzel eingeben.")

    try:
        result = evaluate_stock(ticker=ticker, period=period)

        data = {
            "name": result.stock.name,
            "ticker": result.stock.ticker,
            "currency": result.stock.currency,
            "current_price": result.technical.current_price,
            "combined_score": result.combined_score,
            "signal": result.signal.value,
            "technical": {
                "score": result.technical.score,
                "rsi": result.technical.rsi,
                "rsi_signal": result.technical.rsi_signal,
                "macd": result.technical.macd,
                "macd_signal": result.technical.macd_signal,
                "macd_histogram": result.technical.macd_histogram,
                "sma_50": result.technical.sma_50,
                "sma_200": result.technical.sma_200,
                "sma_signal": result.technical.sma_signal,
                "bollinger_upper": result.technical.bollinger_upper,
                "bollinger_middle": result.technical.bollinger_middle,
                "bollinger_lower": result.technical.bollinger_lower,
                "bollinger_signal": result.technical.bollinger_signal,
                "volume_trend": result.technical.volume_trend,
            },
            "fundamental": {
                "score": result.fundamental.score,
                "pe_ratio": result.fundamental.pe_ratio,
                "forward_pe": result.fundamental.forward_pe,
                "pb_ratio": result.fundamental.pb_ratio,
                "ps_ratio": result.fundamental.ps_ratio,
                "peg_ratio": result.fundamental.peg_ratio,
                "profit_margin": result.fundamental.profit_margin,
                "roe": result.fundamental.roe,
                "roa": result.fundamental.roa,
                "dividend_yield": result.fundamental.dividend_yield,
                "payout_ratio": result.fundamental.payout_ratio,
                "revenue_growth": result.fundamental.revenue_growth,
                "earnings_growth": result.fundamental.earnings_growth,
                "debt_to_equity": result.fundamental.debt_to_equity,
                "current_ratio": result.fundamental.current_ratio,
                "target_price": result.fundamental.target_price,
                "recommendation": result.fundamental.recommendation,
            },
        }

        return render_template("index.html", result=data)

    except ValueError as e:
        return render_template("index.html", error=str(e))
    except Exception as e:
        return render_template("index.html", error=f"Fehler: {e}")


def _format_size(size_bytes: int) -> str:
    """Formatiert Bytes in lesbare Größe."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def _count_by_action(activities: list, action: str) -> int:
    """Zählt Aktivitäten nach Aktion."""
    return sum(1 for a in activities if a.action == action)


@app.route("/admin/sharepoint")
def admin_sharepoint():
    """Admin-Seite: SharePoint-Datentransfers anzeigen."""
    config = SharePointConfig.from_env()
    demo_mode = not config.is_configured

    if demo_mode:
        report = get_demo_report()
    else:
        client = SharePointClient(config)
        report = client.get_recent_activities()

    return render_template(
        "admin.html",
        report=report,
        demo_mode=demo_mode,
        format_size=_format_size,
        count_by_action=_count_by_action,
    )


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Startet den Webserver."""
    app.run(host=host, port=port, debug=debug)
