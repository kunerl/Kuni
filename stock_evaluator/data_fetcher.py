"""Modul zum Abrufen von Aktiendaten über yfinance."""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class StockData:
    """Container für abgerufene Aktiendaten."""

    ticker: str
    history: pd.DataFrame
    info: dict
    currency: str
    name: str


def fetch_stock_data(ticker: str, period: str = "1y") -> StockData:
    """Ruft historische Kursdaten und Fundamentaldaten einer Aktie ab.

    Args:
        ticker: Das Börsenkürzel (z.B. "AAPL", "SAP.DE").
        period: Zeitraum für historische Daten (z.B. "6mo", "1y", "2y").

    Returns:
        StockData mit historischen Kursen und Unternehmensinformationen.

    Raises:
        ValueError: Wenn der Ticker ungültig ist oder keine Daten gefunden werden.
    """
    import yfinance as yf

    stock = yf.Ticker(ticker)
    history = stock.history(period=period)

    if history.empty:
        raise ValueError(
            f"Keine Daten für Ticker '{ticker}' gefunden. "
            "Bitte prüfe das Börsenkürzel."
        )

    info = stock.info
    currency = info.get("currency", "USD")
    name = info.get("longName", info.get("shortName", ticker))

    return StockData(
        ticker=ticker.upper(),
        history=history,
        info=info,
        currency=currency,
        name=name,
    )
