"""Tests für die technische Analyse."""

import numpy as np
import pandas as pd
import pytest

from stock_evaluator.technical_analysis import (
    TechnicalSignals,
    calculate_bollinger_bands,
    calculate_macd,
    calculate_rsi,
    analyze_volume_trend,
    run_technical_analysis,
)


def _make_price_series(values: list[float]) -> pd.Series:
    """Erstellt eine Pandas-Series aus einer Liste von Werten."""
    return pd.Series(values, dtype=float)


def _make_history(close_prices: list[float], volumes: list[float] | None = None) -> pd.DataFrame:
    """Erstellt ein minimales DataFrame wie es von yfinance kommt."""
    n = len(close_prices)
    if volumes is None:
        volumes = [1_000_000.0] * n
    return pd.DataFrame({
        "Close": close_prices,
        "Volume": volumes,
        "Open": close_prices,
        "High": [p * 1.02 for p in close_prices],
        "Low": [p * 0.98 for p in close_prices],
    })


class TestRSI:
    def test_rsi_returns_series(self):
        prices = _make_price_series(list(range(100, 130)))
        rsi = calculate_rsi(prices)
        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(prices)

    def test_rsi_range(self):
        """RSI sollte zwischen 0 und 100 liegen."""
        np.random.seed(42)
        prices = _make_price_series(np.cumsum(np.random.randn(100)) + 100)
        rsi = calculate_rsi(prices).dropna()
        assert rsi.min() >= 0
        assert rsi.max() <= 100

    def test_rsi_rising_prices(self):
        """Bei stetig steigenden Preisen sollte RSI hoch sein."""
        prices = _make_price_series([100 + i * 2 for i in range(30)])
        rsi = calculate_rsi(prices)
        assert rsi.iloc[-1] > 70

    def test_rsi_falling_prices(self):
        """Bei stetig fallenden Preisen sollte RSI niedrig sein."""
        prices = _make_price_series([200 - i * 2 for i in range(30)])
        rsi = calculate_rsi(prices)
        assert rsi.iloc[-1] < 30


class TestMACD:
    def test_macd_returns_three_series(self):
        prices = _make_price_series(list(range(100, 150)))
        macd, signal, histogram = calculate_macd(prices)
        assert isinstance(macd, pd.Series)
        assert isinstance(signal, pd.Series)
        assert isinstance(histogram, pd.Series)

    def test_histogram_equals_difference(self):
        prices = _make_price_series(list(range(100, 150)))
        macd, signal, histogram = calculate_macd(prices)
        diff = macd - signal
        pd.testing.assert_series_equal(histogram, diff, check_names=False)


class TestBollingerBands:
    def test_upper_above_lower(self):
        prices = _make_price_series([100 + i * 0.5 for i in range(30)])
        upper, middle, lower = calculate_bollinger_bands(prices)
        valid = upper.dropna()
        valid_lower = lower.dropna()
        assert (valid >= valid_lower).all()

    def test_middle_is_sma(self):
        prices = _make_price_series([100 + i for i in range(30)])
        _, middle, _ = calculate_bollinger_bands(prices, period=20)
        sma = prices.rolling(window=20).mean()
        pd.testing.assert_series_equal(middle, sma, check_names=False)


class TestVolumeTrend:
    def test_rising_volume(self):
        vols = [100_000] * 20 + [200_000] * 20
        result = analyze_volume_trend(pd.Series(vols), period=20)
        assert result == "steigend"

    def test_falling_volume(self):
        vols = [200_000] * 20 + [100_000] * 20
        result = analyze_volume_trend(pd.Series(vols), period=20)
        assert result == "fallend"

    def test_stable_volume(self):
        vols = [100_000] * 40
        result = analyze_volume_trend(pd.Series(vols), period=20)
        assert result == "stabil"


class TestRunTechnicalAnalysis:
    def test_returns_technical_signals(self):
        np.random.seed(42)
        prices = list(np.cumsum(np.random.randn(250)) + 150)
        volumes = [1_000_000 + np.random.randint(-100_000, 100_000) for _ in range(250)]
        history = _make_history(prices, volumes)

        result = run_technical_analysis(history)

        assert isinstance(result, TechnicalSignals)
        assert 0 <= result.rsi <= 100
        assert result.rsi_signal in ("überverkauft", "neutral", "überkauft")
        assert result.macd_signal in ("bullisch", "neutral", "bärisch")
        assert result.sma_signal in ("bullisch", "bärisch")
        assert result.bollinger_signal in ("überverkauft", "neutral", "überkauft")
        assert result.volume_trend in ("steigend", "fallend", "stabil")
        assert -100 <= result.score <= 100
