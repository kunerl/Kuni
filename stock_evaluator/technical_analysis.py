"""Technische Analyse-Indikatoren für Aktienbewertung."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class TechnicalSignals:
    """Ergebnis der technischen Analyse."""

    rsi: float
    rsi_signal: str  # "überverkauft", "neutral", "überkauft"
    macd: float
    macd_signal_line: float
    macd_histogram: float
    macd_signal: str  # "bullisch", "neutral", "bärisch"
    sma_50: float
    sma_200: float
    sma_signal: str  # "bullisch" (Golden Cross), "bärisch" (Death Cross)
    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float
    bollinger_signal: str  # "überverkauft", "neutral", "überkauft"
    current_price: float
    volume_trend: str  # "steigend", "fallend", "stabil"
    score: float  # -100 bis +100


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Berechnet den Relative Strength Index (RSI)."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Verwende Wilder's Smoothing nach der initialen SMA-Berechnung
    for i in range(period, len(avg_gain)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Berechnet MACD, Signal-Linie und Histogramm."""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    prices: pd.Series, period: int = 20, std_dev: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Berechnet Bollinger Bänder (oberes, mittleres, unteres Band)."""
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower


def analyze_volume_trend(volume: pd.Series, period: int = 20) -> str:
    """Analysiert den Volumen-Trend."""
    if len(volume) < period * 2:
        return "stabil"

    recent_avg = volume.tail(period).mean()
    previous_avg = volume.iloc[-period * 2 : -period].mean()

    if previous_avg == 0:
        return "stabil"

    change = (recent_avg - previous_avg) / previous_avg
    if change > 0.15:
        return "steigend"
    elif change < -0.15:
        return "fallend"
    return "stabil"


def run_technical_analysis(history: pd.DataFrame) -> TechnicalSignals:
    """Führt eine vollständige technische Analyse durch.

    Args:
        history: DataFrame mit Spalten 'Close', 'Volume' (von yfinance).

    Returns:
        TechnicalSignals mit allen berechneten Indikatoren und Signalen.
    """
    close = history["Close"]
    current_price = float(close.iloc[-1])

    # RSI
    rsi_series = calculate_rsi(close)
    rsi_value = float(rsi_series.iloc[-1])
    if rsi_value < 30:
        rsi_signal = "überverkauft"
    elif rsi_value > 70:
        rsi_signal = "überkauft"
    else:
        rsi_signal = "neutral"

    # MACD
    macd_line, signal_line, histogram = calculate_macd(close)
    macd_val = float(macd_line.iloc[-1])
    macd_sig = float(signal_line.iloc[-1])
    macd_hist = float(histogram.iloc[-1])
    if macd_hist > 0 and macd_val > macd_sig:
        macd_signal = "bullisch"
    elif macd_hist < 0 and macd_val < macd_sig:
        macd_signal = "bärisch"
    else:
        macd_signal = "neutral"

    # Moving Averages
    sma_50 = float(close.rolling(window=50).mean().iloc[-1])
    sma_200_series = close.rolling(window=200).mean()
    sma_200 = float(sma_200_series.iloc[-1]) if not np.isnan(sma_200_series.iloc[-1]) else sma_50
    if sma_50 > sma_200:
        sma_signal = "bullisch"
    else:
        sma_signal = "bärisch"

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)
    bb_up = float(bb_upper.iloc[-1])
    bb_mid = float(bb_middle.iloc[-1])
    bb_low = float(bb_lower.iloc[-1])
    if current_price <= bb_low:
        bb_signal = "überverkauft"
    elif current_price >= bb_up:
        bb_signal = "überkauft"
    else:
        bb_signal = "neutral"

    # Volumen
    volume_trend = analyze_volume_trend(history["Volume"])

    # Gesamtscore berechnen (-100 bis +100)
    score = _calculate_technical_score(
        rsi_value, rsi_signal, macd_signal, sma_signal, bb_signal, volume_trend
    )

    return TechnicalSignals(
        rsi=round(rsi_value, 2),
        rsi_signal=rsi_signal,
        macd=round(macd_val, 4),
        macd_signal_line=round(macd_sig, 4),
        macd_histogram=round(macd_hist, 4),
        macd_signal=macd_signal,
        sma_50=round(sma_50, 2),
        sma_200=round(sma_200, 2),
        sma_signal=sma_signal,
        bollinger_upper=round(bb_up, 2),
        bollinger_middle=round(bb_mid, 2),
        bollinger_lower=round(bb_low, 2),
        bollinger_signal=bb_signal,
        current_price=round(current_price, 2),
        volume_trend=volume_trend,
        score=round(score, 1),
    )


def _calculate_technical_score(
    rsi: float,
    rsi_signal: str,
    macd_signal: str,
    sma_signal: str,
    bb_signal: str,
    volume_trend: str,
) -> float:
    """Berechnet einen Gesamtscore aus den technischen Indikatoren.

    Score-Bereich: -100 (stark bärisch) bis +100 (stark bullisch).
    """
    score = 0.0

    # RSI (Gewicht: 25)
    if rsi_signal == "überverkauft":
        score += 25  # Kaufsignal
    elif rsi_signal == "überkauft":
        score -= 25  # Verkaufssignal
    else:
        # Linear skalieren: 50 = 0, <50 positiv, >50 negativ
        score += (50 - rsi) * 0.5

    # MACD (Gewicht: 25)
    if macd_signal == "bullisch":
        score += 25
    elif macd_signal == "bärisch":
        score -= 25

    # SMA Cross (Gewicht: 25)
    if sma_signal == "bullisch":
        score += 25
    else:
        score -= 25

    # Bollinger Bands (Gewicht: 15)
    if bb_signal == "überverkauft":
        score += 15
    elif bb_signal == "überkauft":
        score -= 15

    # Volumen (Gewicht: 10)
    if volume_trend == "steigend":
        score += 10
    elif volume_trend == "fallend":
        score -= 5

    return max(-100, min(100, score))
