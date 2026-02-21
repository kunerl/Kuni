"""Fundamentalanalyse für Aktienbewertung."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FundamentalSignals:
    """Ergebnis der Fundamentalanalyse."""

    # Bewertungskennzahlen
    pe_ratio: Optional[float]  # Kurs-Gewinn-Verhältnis (KGV)
    forward_pe: Optional[float]  # Erwartetes KGV
    pb_ratio: Optional[float]  # Kurs-Buchwert-Verhältnis (KBV)
    ps_ratio: Optional[float]  # Kurs-Umsatz-Verhältnis (KUV)
    peg_ratio: Optional[float]  # Price/Earnings-to-Growth

    # Rentabilität
    profit_margin: Optional[float]  # Gewinnmarge in %
    roe: Optional[float]  # Eigenkapitalrendite in %
    roa: Optional[float]  # Gesamtkapitalrendite in %

    # Dividende
    dividend_yield: Optional[float]  # Dividendenrendite in %
    payout_ratio: Optional[float]  # Ausschüttungsquote in %

    # Wachstum
    revenue_growth: Optional[float]  # Umsatzwachstum in %
    earnings_growth: Optional[float]  # Gewinnwachstum in %

    # Verschuldung
    debt_to_equity: Optional[float]  # Verschuldungsgrad
    current_ratio: Optional[float]  # Liquiditätsgrad

    # Bewertung
    target_price: Optional[float]  # Analystenpreis-Ziel
    recommendation: Optional[str]  # Analysten-Empfehlung

    score: float  # -100 bis +100


def _safe_get(info: dict, key: str) -> Optional[float]:
    """Liest einen Wert sicher aus dem Info-Dict."""
    val = info.get(key)
    if val is None or val == "Infinity" or val == "NaN":
        return None
    try:
        result = float(val)
        if result != result:  # NaN check
            return None
        return result
    except (ValueError, TypeError):
        return None


def _safe_percent(info: dict, key: str) -> Optional[float]:
    """Liest einen Prozentwert und konvertiert ihn."""
    val = _safe_get(info, key)
    if val is not None:
        return round(val * 100, 2)
    return None


def run_fundamental_analysis(info: dict) -> FundamentalSignals:
    """Führt eine Fundamentalanalyse basierend auf Unternehmensdaten durch.

    Args:
        info: Dictionary mit Unternehmensdaten (von yfinance ticker.info).

    Returns:
        FundamentalSignals mit allen Kennzahlen und Gesamtbewertung.
    """
    pe_ratio = _safe_get(info, "trailingPE")
    forward_pe = _safe_get(info, "forwardPE")
    pb_ratio = _safe_get(info, "priceToBook")
    ps_ratio = _safe_get(info, "priceToSalesTrailing12Months")
    peg_ratio = _safe_get(info, "pegRatio")

    profit_margin = _safe_percent(info, "profitMargins")
    roe = _safe_percent(info, "returnOnEquity")
    roa = _safe_percent(info, "returnOnAssets")

    dividend_yield = _safe_percent(info, "dividendYield")
    payout_ratio = _safe_percent(info, "payoutRatio")

    revenue_growth = _safe_percent(info, "revenueGrowth")
    earnings_growth = _safe_percent(info, "earningsGrowth")

    debt_to_equity = _safe_get(info, "debtToEquity")
    current_ratio = _safe_get(info, "currentRatio")

    target_price = _safe_get(info, "targetMeanPrice")
    recommendation = info.get("recommendationKey")

    score = _calculate_fundamental_score(
        pe_ratio=pe_ratio,
        forward_pe=forward_pe,
        pb_ratio=pb_ratio,
        peg_ratio=peg_ratio,
        profit_margin=profit_margin,
        roe=roe,
        dividend_yield=dividend_yield,
        revenue_growth=revenue_growth,
        earnings_growth=earnings_growth,
        debt_to_equity=debt_to_equity,
        current_ratio=current_ratio,
        target_price=target_price,
        current_price=_safe_get(info, "currentPrice"),
        recommendation=recommendation,
    )

    return FundamentalSignals(
        pe_ratio=_round_opt(pe_ratio),
        forward_pe=_round_opt(forward_pe),
        pb_ratio=_round_opt(pb_ratio),
        ps_ratio=_round_opt(ps_ratio),
        peg_ratio=_round_opt(peg_ratio),
        profit_margin=profit_margin,
        roe=roe,
        roa=roa,
        dividend_yield=dividend_yield,
        payout_ratio=payout_ratio,
        revenue_growth=revenue_growth,
        earnings_growth=earnings_growth,
        debt_to_equity=_round_opt(debt_to_equity),
        current_ratio=_round_opt(current_ratio),
        target_price=_round_opt(target_price),
        recommendation=recommendation,
        score=round(score, 1),
    )


def _round_opt(val: Optional[float], decimals: int = 2) -> Optional[float]:
    """Rundet einen optionalen Wert."""
    if val is None:
        return None
    return round(val, decimals)


def _calculate_fundamental_score(
    pe_ratio: Optional[float],
    forward_pe: Optional[float],
    pb_ratio: Optional[float],
    peg_ratio: Optional[float],
    profit_margin: Optional[float],
    roe: Optional[float],
    dividend_yield: Optional[float],
    revenue_growth: Optional[float],
    earnings_growth: Optional[float],
    debt_to_equity: Optional[float],
    current_ratio: Optional[float],
    target_price: Optional[float],
    current_price: Optional[float],
    recommendation: Optional[str],
) -> float:
    """Berechnet den fundamentalen Gesamtscore (-100 bis +100)."""
    score = 0.0
    weight_sum = 0.0

    # KGV-Bewertung (Gewicht: 15)
    if pe_ratio is not None and pe_ratio > 0:
        weight_sum += 15
        if pe_ratio < 10:
            score += 15  # Günstig
        elif pe_ratio < 15:
            score += 10
        elif pe_ratio < 20:
            score += 5
        elif pe_ratio < 30:
            score -= 5
        else:
            score -= 15  # Teuer

    # PEG Ratio (Gewicht: 10)
    if peg_ratio is not None and peg_ratio > 0:
        weight_sum += 10
        if peg_ratio < 1.0:
            score += 10  # Unterbewertet relativ zum Wachstum
        elif peg_ratio < 1.5:
            score += 5
        elif peg_ratio < 2.0:
            score -= 2
        else:
            score -= 10

    # KBV (Gewicht: 10)
    if pb_ratio is not None and pb_ratio > 0:
        weight_sum += 10
        if pb_ratio < 1.0:
            score += 10
        elif pb_ratio < 2.0:
            score += 5
        elif pb_ratio < 4.0:
            score -= 2
        else:
            score -= 10

    # Eigenkapitalrendite (Gewicht: 15)
    if roe is not None:
        weight_sum += 15
        if roe > 20:
            score += 15
        elif roe > 15:
            score += 10
        elif roe > 10:
            score += 5
        elif roe > 0:
            score -= 5
        else:
            score -= 15

    # Gewinnmarge (Gewicht: 10)
    if profit_margin is not None:
        weight_sum += 10
        if profit_margin > 20:
            score += 10
        elif profit_margin > 10:
            score += 5
        elif profit_margin > 5:
            score += 2
        elif profit_margin > 0:
            score -= 5
        else:
            score -= 10

    # Dividendenrendite (Gewicht: 10)
    if dividend_yield is not None:
        weight_sum += 10
        if dividend_yield > 5:
            score += 8  # Hohe Dividende, aber Vorsicht
        elif dividend_yield > 3:
            score += 10
        elif dividend_yield > 1.5:
            score += 5
        elif dividend_yield > 0:
            score += 2

    # Umsatzwachstum (Gewicht: 10)
    if revenue_growth is not None:
        weight_sum += 10
        if revenue_growth > 20:
            score += 10
        elif revenue_growth > 10:
            score += 7
        elif revenue_growth > 0:
            score += 3
        else:
            score -= 10

    # Verschuldungsgrad (Gewicht: 10)
    if debt_to_equity is not None:
        weight_sum += 10
        if debt_to_equity < 30:
            score += 10
        elif debt_to_equity < 60:
            score += 5
        elif debt_to_equity < 100:
            score -= 2
        elif debt_to_equity < 200:
            score -= 7
        else:
            score -= 10

    # Analysten-Kursziel (Gewicht: 10)
    if target_price is not None and current_price is not None and current_price > 0:
        weight_sum += 10
        upside = ((target_price - current_price) / current_price) * 100
        if upside > 20:
            score += 10
        elif upside > 10:
            score += 7
        elif upside > 0:
            score += 3
        elif upside > -10:
            score -= 3
        else:
            score -= 10

    # Normalisierung auf -100 bis +100
    if weight_sum > 0:
        score = (score / weight_sum) * 100

    return max(-100, min(100, score))
