"""Tests für die Fundamentalanalyse."""

import pytest

from stock_evaluator.fundamental_analysis import (
    FundamentalSignals,
    run_fundamental_analysis,
    _safe_get,
    _safe_percent,
)


class TestSafeGet:
    def test_valid_float(self):
        assert _safe_get({"key": 42.5}, "key") == 42.5

    def test_valid_int(self):
        assert _safe_get({"key": 10}, "key") == 10.0

    def test_none_value(self):
        assert _safe_get({"key": None}, "key") is None

    def test_missing_key(self):
        assert _safe_get({}, "key") is None

    def test_infinity_string(self):
        assert _safe_get({"key": "Infinity"}, "key") is None

    def test_nan_string(self):
        assert _safe_get({"key": "NaN"}, "key") is None

    def test_nan_float(self):
        assert _safe_get({"key": float("nan")}, "key") is None


class TestSafePercent:
    def test_converts_to_percent(self):
        assert _safe_percent({"key": 0.15}, "key") == 15.0

    def test_none_stays_none(self):
        assert _safe_percent({"key": None}, "key") is None


GOOD_STOCK_INFO = {
    "trailingPE": 15.0,
    "forwardPE": 12.0,
    "priceToBook": 2.5,
    "priceToSalesTrailing12Months": 3.0,
    "pegRatio": 1.2,
    "profitMargins": 0.18,
    "returnOnEquity": 0.22,
    "returnOnAssets": 0.10,
    "dividendYield": 0.025,
    "payoutRatio": 0.35,
    "revenueGrowth": 0.15,
    "earningsGrowth": 0.20,
    "debtToEquity": 45.0,
    "currentRatio": 1.8,
    "targetMeanPrice": 180.0,
    "currentPrice": 150.0,
    "recommendationKey": "buy",
}

WEAK_STOCK_INFO = {
    "trailingPE": 80.0,
    "forwardPE": 60.0,
    "priceToBook": 10.0,
    "priceToSalesTrailing12Months": 15.0,
    "pegRatio": 3.5,
    "profitMargins": -0.05,
    "returnOnEquity": -0.08,
    "returnOnAssets": -0.03,
    "dividendYield": None,
    "payoutRatio": None,
    "revenueGrowth": -0.10,
    "earningsGrowth": -0.15,
    "debtToEquity": 250.0,
    "currentRatio": 0.6,
    "targetMeanPrice": 30.0,
    "currentPrice": 50.0,
    "recommendationKey": "sell",
}


class TestFundamentalAnalysis:
    def test_good_stock_positive_score(self):
        result = run_fundamental_analysis(GOOD_STOCK_INFO)
        assert isinstance(result, FundamentalSignals)
        assert result.score > 0

    def test_weak_stock_negative_score(self):
        result = run_fundamental_analysis(WEAK_STOCK_INFO)
        assert isinstance(result, FundamentalSignals)
        assert result.score < 0

    def test_score_in_range(self):
        result = run_fundamental_analysis(GOOD_STOCK_INFO)
        assert -100 <= result.score <= 100

    def test_empty_info_returns_result(self):
        result = run_fundamental_analysis({})
        assert isinstance(result, FundamentalSignals)
        assert result.pe_ratio is None
        assert result.score == 0.0  # Keine Daten = neutraler Score

    def test_values_correctly_mapped(self):
        result = run_fundamental_analysis(GOOD_STOCK_INFO)
        assert result.pe_ratio == 15.0
        assert result.pb_ratio == 2.5
        assert result.dividend_yield == 2.5  # 0.025 * 100
        assert result.profit_margin == 18.0  # 0.18 * 100
        assert result.recommendation == "buy"
