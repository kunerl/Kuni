"""Tests für die Bewertungs-Engine."""

import pytest

from stock_evaluator.evaluator import Signal, _score_to_signal


class TestScoreToSignal:
    def test_strong_buy(self):
        assert _score_to_signal(75) == Signal.STARKER_KAUF
        assert _score_to_signal(50) == Signal.STARKER_KAUF
        assert _score_to_signal(100) == Signal.STARKER_KAUF

    def test_buy(self):
        assert _score_to_signal(20) == Signal.KAUF
        assert _score_to_signal(35) == Signal.KAUF
        assert _score_to_signal(49) == Signal.KAUF

    def test_hold(self):
        assert _score_to_signal(0) == Signal.HALTEN
        assert _score_to_signal(19) == Signal.HALTEN
        assert _score_to_signal(-20) == Signal.HALTEN

    def test_sell(self):
        assert _score_to_signal(-21) == Signal.VERKAUF
        assert _score_to_signal(-35) == Signal.VERKAUF
        assert _score_to_signal(-50) == Signal.VERKAUF

    def test_strong_sell(self):
        assert _score_to_signal(-51) == Signal.STARKER_VERKAUF
        assert _score_to_signal(-100) == Signal.STARKER_VERKAUF
