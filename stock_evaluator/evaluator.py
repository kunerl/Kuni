"""Bewertungs-Engine: Kombiniert technische und fundamentale Analyse zu einer Empfehlung."""

from dataclasses import dataclass
from enum import Enum

from .data_fetcher import StockData, fetch_stock_data
from .fundamental_analysis import FundamentalSignals, run_fundamental_analysis
from .technical_analysis import TechnicalSignals, run_technical_analysis


class Signal(Enum):
    """Kauf-/Verkaufssignal."""

    STARKER_KAUF = "STARKER KAUF"
    KAUF = "KAUF"
    HALTEN = "HALTEN"
    VERKAUF = "VERKAUF"
    STARKER_VERKAUF = "STARKER VERKAUF"


@dataclass
class Evaluation:
    """Gesamtergebnis der Aktienbewertung."""

    stock: StockData
    technical: TechnicalSignals
    fundamental: FundamentalSignals
    combined_score: float  # -100 bis +100
    signal: Signal
    summary: str


def evaluate_stock(
    ticker: str,
    period: str = "1y",
    technical_weight: float = 0.4,
    fundamental_weight: float = 0.6,
) -> Evaluation:
    """Bewertet eine Aktie anhand technischer und fundamentaler Kriterien.

    Args:
        ticker: Börsenkürzel (z.B. "AAPL", "MSFT", "SAP.DE").
        period: Zeitraum für historische Daten.
        technical_weight: Gewichtung der technischen Analyse (0-1).
        fundamental_weight: Gewichtung der Fundamentalanalyse (0-1).

    Returns:
        Evaluation mit kombinierter Bewertung und Kauf-/Verkaufsempfehlung.
    """
    stock_data = fetch_stock_data(ticker, period)
    technical = run_technical_analysis(stock_data.history)
    fundamental = run_fundamental_analysis(stock_data.info)

    # Gewichteter Gesamtscore
    total_weight = technical_weight + fundamental_weight
    combined_score = (
        (technical.score * technical_weight + fundamental.score * fundamental_weight)
        / total_weight
    )
    combined_score = round(combined_score, 1)

    signal = _score_to_signal(combined_score)
    summary = _build_summary(stock_data, technical, fundamental, combined_score, signal)

    return Evaluation(
        stock=stock_data,
        technical=technical,
        fundamental=fundamental,
        combined_score=combined_score,
        signal=signal,
        summary=summary,
    )


def _score_to_signal(score: float) -> Signal:
    """Wandelt den Score in ein Kauf-/Verkaufssignal um."""
    if score >= 50:
        return Signal.STARKER_KAUF
    elif score >= 20:
        return Signal.KAUF
    elif score >= -20:
        return Signal.HALTEN
    elif score >= -50:
        return Signal.VERKAUF
    else:
        return Signal.STARKER_VERKAUF


def _build_summary(
    stock: StockData,
    tech: TechnicalSignals,
    fund: FundamentalSignals,
    score: float,
    signal: Signal,
) -> str:
    """Erstellt eine lesbare Zusammenfassung der Bewertung."""
    lines = [
        f"{'=' * 60}",
        f"  AKTIEN-BEWERTUNG: {stock.name} ({stock.ticker})",
        f"{'=' * 60}",
        f"",
        f"  Aktueller Kurs: {tech.current_price} {stock.currency}",
        f"",
        f"  --- TECHNISCHE ANALYSE (Score: {tech.score:+.1f}) ---",
        f"",
        f"  RSI (14):          {tech.rsi:>8.2f}  [{tech.rsi_signal}]",
        f"  MACD:              {tech.macd:>8.4f}  [{tech.macd_signal}]",
        f"  MACD Signal:       {tech.macd_signal_line:>8.4f}",
        f"  MACD Histogramm:   {tech.macd_histogram:>8.4f}",
        f"  SMA 50:            {tech.sma_50:>8.2f}",
        f"  SMA 200:           {tech.sma_200:>8.2f}  [{tech.sma_signal}]",
        f"  Bollinger Oben:    {tech.bollinger_upper:>8.2f}",
        f"  Bollinger Mitte:   {tech.bollinger_middle:>8.2f}",
        f"  Bollinger Unten:   {tech.bollinger_lower:>8.2f}  [{tech.bollinger_signal}]",
        f"  Volumen-Trend:     {tech.volume_trend}",
        f"",
        f"  --- FUNDAMENTALANALYSE (Score: {fund.score:+.1f}) ---",
        f"",
    ]

    def _fmt(label: str, value, suffix: str = "") -> str:
        if value is None:
            return f"  {label:<22} {'k.A.':>8}"
        return f"  {label:<22} {value:>8}{suffix}"

    lines.extend([
        _fmt("KGV (trailing):", fund.pe_ratio),
        _fmt("KGV (forward):", fund.forward_pe),
        _fmt("KBV:", fund.pb_ratio),
        _fmt("KUV:", fund.ps_ratio),
        _fmt("PEG Ratio:", fund.peg_ratio),
        _fmt("Gewinnmarge:", fund.profit_margin, "%"),
        _fmt("Eigenkapitalrendite:", fund.roe, "%"),
        _fmt("Gesamtkapitalrendite:", fund.roa, "%"),
        _fmt("Dividendenrendite:", fund.dividend_yield, "%"),
        _fmt("Ausschüttungsquote:", fund.payout_ratio, "%"),
        _fmt("Umsatzwachstum:", fund.revenue_growth, "%"),
        _fmt("Gewinnwachstum:", fund.earnings_growth, "%"),
        _fmt("Verschuldungsgrad:", fund.debt_to_equity),
        _fmt("Liquiditätsgrad:", fund.current_ratio),
        _fmt("Analysten-Kursziel:", fund.target_price, f" {stock.currency}"),
        f"  Analysten-Empfehlung: {fund.recommendation or 'k.A.'}",
    ])

    lines.extend([
        f"",
        f"  {'=' * 56}",
        f"  GESAMTBEWERTUNG",
        f"  {'=' * 56}",
        f"",
        f"  Technischer Score:     {tech.score:>+7.1f}  (Gewicht: 40%)",
        f"  Fundamentaler Score:   {fund.score:>+7.1f}  (Gewicht: 60%)",
        f"  Kombinierter Score:    {score:>+7.1f}",
        f"",
        f"  >>> EMPFEHLUNG: {signal.value} <<<",
        f"",
        f"  Score-Skala:",
        f"    +50 bis +100  = STARKER KAUF",
        f"    +20 bis  +49  = KAUF",
        f"    -20 bis  +19  = HALTEN",
        f"    -49 bis  -21  = VERKAUF",
        f"   -100 bis  -50  = STARKER VERKAUF",
        f"",
        f"  HINWEIS: Diese Analyse dient nur zu Informationszwecken",
        f"  und stellt keine Anlageberatung dar.",
        f"{'=' * 60}",
    ])

    return "\n".join(lines)
