"""
Screener API Routes - Value investing stock screener endpoints.
"""

from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from backend.models.responses import ScreenerResponse, ScreenedStock, ScreenerScore
from storage.json_store import JsonStore
from services.metrics_service import MetricsService

router = APIRouter(prefix="/screener", tags=["screener"])


def get_json_store() -> JsonStore:
    """Dependency for JSON store."""
    return JsonStore()


def get_metrics_service(store: JsonStore = Depends(get_json_store)) -> MetricsService:
    """Dependency for metrics service."""
    return MetricsService(store)


def score_metric(value: float | None, target_min: float | None = None, target_max: float | None = None,
                  inverse: bool = False) -> tuple[float, bool]:
    """
    Score a metric on a 0-1 scale where 1 is best.

    Args:
        value: The metric value to score
        target_min: Minimum acceptable value (if applicable)
        target_max: Maximum acceptable value (if applicable)
        inverse: If True, lower values are better

    Returns:
        Tuple of (score, passes_criteria)
    """
    if value is None:
        return (0.0, False)

    # For inverse metrics (lower is better, like P/E, Debt/Equity)
    if inverse and target_max is not None:
        if value <= target_max:
            # Perfect score if at or below target
            score = min(1.0, target_max / max(value, 0.01))
            passes = True
        else:
            # Partial score for being close
            score = max(0.0, target_max / value)
            passes = False
        return (score, passes)

    # For normal metrics (higher is better, like ROE, Current Ratio)
    if not inverse and target_min is not None:
        if value >= target_min:
            # Scale beyond target gets full marks
            score = min(1.0, value / target_min) if target_min != 0 else 1.0
            passes = True
        else:
            # Partial score for being close
            score = value / target_min if target_min != 0 else 0.0
            passes = False
        return (score, passes)

    return (0.5, False)  # Default for unclear criteria


@router.get("/value", response_model=ScreenerResponse)
async def get_value_screener(
    store: JsonStore = Depends(get_json_store),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """
    Screen all stocks in watchlist using Buffett/Munger value investing criteria.

    Returns stocks ranked by overall score (0-1 scale) based on:

    Core Criteria:
    - P/E Ratio (< 20)
    - P/B Ratio (< 3.0)
    - PEG Ratio (< 1.0)
    - ROE (> 15%)
    - Debt-to-Equity (< 0.5)
    - Current Ratio (> 1.5)
    - Earnings Stability (80%+ positive years)
    - Dividend History (5+ consecutive years)
    - Operating Margin (> 10%)
    - Piotroski F-Score (>= 7)

    Buffett/Munger Criteria:
    - Gross Profit Margin (> 40%)
    - Price to FCF (< 15)
    - FCF Yield (> 5%)
    - Quality of Earnings (> 1.0)
    - CROIC (> 15%)
    - Altman Z-Score (> 3.0)
    - Debt to EBITDA (< 3.0)
    - LT Debt to Earnings (< 4 years)
    - SG&A to Gross Profit (< 80%)
    - Return on Tangible Equity (> 15%)
    - Graham Number (undervalued if margin > 0%)
    """
    # Get watchlist
    watchlist = store.load_watchlist("default")

    if not watchlist or not watchlist.tickers:
        return ScreenerResponse(
            stocks=[],
            screened_at=datetime.now().isoformat(),
            criteria_count=0
        )

    screened_stocks: List[ScreenedStock] = []

    for ticker_entry in watchlist.tickers:
        ticker = ticker_entry.symbol

        try:
            # Get metrics for this stock
            metrics_snapshot = metrics_service.json_store.read_metrics_snapshot(ticker)
            raw_snapshot = metrics_service.json_store.read_raw_snapshot(ticker)

            if not metrics_snapshot or not raw_snapshot:
                continue

            scores: List[ScreenerScore] = []

            # Extract metrics
            valuation = metrics_snapshot.valuation or {}
            profitability = metrics_snapshot.profitability or {}
            financial_strength = metrics_snapshot.financial_strength or {}
            capital_allocation = metrics_snapshot.capital_allocation or {}
            moat = metrics_snapshot.moat or {}

            # 1. P/E Ratio (target < 20)
            pe = valuation.get('price_to_earnings')
            pe_score, pe_passes = score_metric(pe, target_max=20, inverse=True)
            scores.append(ScreenerScore(
                metric_name="P/E Ratio",
                value=pe,
                score=pe_score,
                passes=pe_passes,
                target="< 20"
            ))

            # 2. P/B Ratio (target < 3.0)
            pb = valuation.get('price_to_book')
            pb_score, pb_passes = score_metric(pb, target_max=3.0, inverse=True)
            scores.append(ScreenerScore(
                metric_name="P/B Ratio",
                value=pb,
                score=pb_score,
                passes=pb_passes,
                target="< 3.0"
            ))

            # 3. PEG Ratio (target < 1.0)
            peg = valuation.get('peg_ratio')
            peg_score, peg_passes = score_metric(peg, target_max=1.0, inverse=True)
            scores.append(ScreenerScore(
                metric_name="PEG Ratio",
                value=peg,
                score=peg_score,
                passes=peg_passes,
                target="< 1.0"
            ))

            # 4. ROE (target > 15%)
            roe = profitability.get('return_on_equity')
            roe_score, roe_passes = score_metric(roe, target_min=0.15, inverse=False)
            scores.append(ScreenerScore(
                metric_name="ROE",
                value=roe,
                score=roe_score,
                passes=roe_passes,
                target="> 15%"
            ))

            # 5. Debt-to-Equity (target < 0.5)
            de_data = financial_strength.get('debt_to_equity_and_interest_coverage', {})
            de = de_data.get('debt_to_equity') if isinstance(de_data, dict) else None
            de_score, de_passes = score_metric(de, target_max=0.5, inverse=True)
            scores.append(ScreenerScore(
                metric_name="Debt/Equity",
                value=de,
                score=de_score,
                passes=de_passes,
                target="< 0.5"
            ))

            # 6. Current Ratio (target > 1.5)
            cr = financial_strength.get('current_ratio')
            cr_score, cr_passes = score_metric(cr, target_min=1.5, inverse=False)
            scores.append(ScreenerScore(
                metric_name="Current Ratio",
                value=cr,
                score=cr_score,
                passes=cr_passes,
                target="> 1.5"
            ))

            # 7. Earnings Stability (target: meets_criteria = True)
            earnings_stability = profitability.get('earnings_stability', {})
            if isinstance(earnings_stability, dict):
                meets_criteria = earnings_stability.get('meets_criteria', False)
                stability_pct = earnings_stability.get('stability_percentage', 0)
                es_score = stability_pct
                es_passes = meets_criteria
            else:
                es_score, es_passes = 0.0, False
            scores.append(ScreenerScore(
                metric_name="Earnings Stability",
                value=stability_pct if isinstance(earnings_stability, dict) else None,
                score=es_score,
                passes=es_passes,
                target="80%+ positive"
            ))

            # 8. Dividend History (target: 5+ years)
            div_history = capital_allocation.get('dividend_history', {})
            if isinstance(div_history, dict):
                meets_5year = div_history.get('meets_5year_criteria', False)
                consec_years = div_history.get('consecutive_years', 0)
                dh_score = min(1.0, consec_years / 5.0) if consec_years else 0.0
                dh_passes = meets_5year
            else:
                dh_score, dh_passes = 0.0, False
            scores.append(ScreenerScore(
                metric_name="Dividend History",
                value=consec_years if isinstance(div_history, dict) else None,
                score=dh_score,
                passes=dh_passes,
                target="5+ years"
            ))

            # 9. Operating Margin (target > 10%)
            op_margin_data = profitability.get('operating_and_net_margin', {})
            op_margin = op_margin_data.get('operating_margin') if isinstance(op_margin_data, dict) else None
            om_score, om_passes = score_metric(op_margin, target_min=0.10, inverse=False)
            scores.append(ScreenerScore(
                metric_name="Operating Margin",
                value=op_margin,
                score=om_score,
                passes=om_passes,
                target="> 10%"
            ))

            # 10. Piotroski F-Score (target >= 7)
            fscore_data = moat.get('piotroski_fscore', {})
            if isinstance(fscore_data, dict):
                fscore = fscore_data.get('score', 0)
                pf_score = fscore / 9.0  # Normalize to 0-1
                pf_passes = fscore >= 7
            else:
                pf_score, pf_passes = 0.0, False
            scores.append(ScreenerScore(
                metric_name="Piotroski F-Score",
                value=fscore if isinstance(fscore_data, dict) else None,
                score=pf_score,
                passes=pf_passes,
                target=">= 7"
            ))

            # ===== Buffett/Munger Additional Criteria =====

            # 11. Gross Profit Margin (target > 40% - Buffett's moat indicator)
            gpm = profitability.get('gross_profit_margin')
            gpm_score, gpm_passes = score_metric(gpm, target_min=0.40, inverse=False)
            scores.append(ScreenerScore(
                metric_name="Gross Profit Margin",
                value=gpm,
                score=gpm_score,
                passes=gpm_passes,
                target="> 40%"
            ))

            # 12. Price to FCF (target < 15 - Buffett's preferred valuation)
            p_fcf = valuation.get('price_to_fcf')
            pfcf_score, pfcf_passes = score_metric(p_fcf, target_max=15.0, inverse=True)
            scores.append(ScreenerScore(
                metric_name="Price to FCF",
                value=p_fcf,
                score=pfcf_score,
                passes=pfcf_passes,
                target="< 15"
            ))

            # 13. FCF Yield (target > 5%)
            fcf_y = valuation.get('fcf_yield')
            fcfy_score, fcfy_passes = score_metric(fcf_y, target_min=0.05, inverse=False)
            scores.append(ScreenerScore(
                metric_name="FCF Yield",
                value=fcf_y,
                score=fcfy_score,
                passes=fcfy_passes,
                target="> 5%"
            ))

            # 14. Quality of Earnings (target > 1.0 - OCF/Net Income)
            qoe = profitability.get('quality_of_earnings')
            qoe_score, qoe_passes = score_metric(qoe, target_min=1.0, inverse=False)
            scores.append(ScreenerScore(
                metric_name="Quality of Earnings",
                value=qoe,
                score=qoe_score,
                passes=qoe_passes,
                target="> 1.0"
            ))

            # 15. Cash Return on Invested Capital (target > 15%)
            croic = profitability.get('cash_return_on_invested_capital')
            croic_score, croic_passes = score_metric(croic, target_min=0.15, inverse=False)
            scores.append(ScreenerScore(
                metric_name="CROIC",
                value=croic,
                score=croic_score,
                passes=croic_passes,
                target="> 15%"
            ))

            # 16. Altman Z-Score (target > 3.0 - safe from bankruptcy)
            z_score = financial_strength.get('altman_z_score')
            zs_score, zs_passes = score_metric(z_score, target_min=3.0, inverse=False)
            scores.append(ScreenerScore(
                metric_name="Altman Z-Score",
                value=z_score,
                score=zs_score,
                passes=zs_passes,
                target="> 3.0"
            ))

            # 17. Debt to EBITDA (target < 3.0)
            d_ebitda = financial_strength.get('debt_to_ebitda')
            de_score2, de_passes2 = score_metric(d_ebitda, target_max=3.0, inverse=True)
            scores.append(ScreenerScore(
                metric_name="Debt/EBITDA",
                value=d_ebitda,
                score=de_score2,
                passes=de_passes2,
                target="< 3.0"
            ))

            # 18. Long-term Debt to Earnings (target < 4 years to pay off)
            ltd_earnings = financial_strength.get('long_term_debt_to_earnings')
            ltd_score, ltd_passes = score_metric(ltd_earnings, target_max=4.0, inverse=True)
            scores.append(ScreenerScore(
                metric_name="LT Debt/Earnings",
                value=ltd_earnings,
                score=ltd_score,
                passes=ltd_passes,
                target="< 4 years"
            ))

            # 19. SG&A to Gross Profit (target < 80% - Munger's efficiency)
            sga_gp = profitability.get('sga_to_gross_profit')
            sga_score, sga_passes = score_metric(sga_gp, target_max=0.80, inverse=True)
            scores.append(ScreenerScore(
                metric_name="SG&A/Gross Profit",
                value=sga_gp,
                score=sga_score,
                passes=sga_passes,
                target="< 80%"
            ))

            # 20. Return on Tangible Equity (target > 15%)
            rote = profitability.get('return_on_tangible_equity')
            rote_score, rote_passes = score_metric(rote, target_min=0.15, inverse=False)
            scores.append(ScreenerScore(
                metric_name="Return on Tangible Equity",
                value=rote,
                score=rote_score,
                passes=rote_passes,
                target="> 15%"
            ))

            # 21. Graham Number (undervalued when margin_of_safety > 0)
            graham_data = valuation.get('graham_number', {})
            if isinstance(graham_data, dict):
                graham_mos = graham_data.get('margin_of_safety')
                gn_score, gn_passes = score_metric(graham_mos, target_min=0.0, inverse=False)
            else:
                graham_mos = None
                gn_score, gn_passes = 0.0, False
            scores.append(ScreenerScore(
                metric_name="Graham Number",
                value=graham_mos,
                score=gn_score,
                passes=gn_passes,
                target="Undervalued (MoS > 0%)"
            ))

            # Calculate overall score
            total_score = sum(s.score for s in scores)
            max_score = len(scores)
            overall_score = total_score / max_score if max_score > 0 else 0.0
            total_points = sum(1 for s in scores if s.passes)

            # Get price and market cap
            price = raw_snapshot.price.get('close') if raw_snapshot.price else None
            market_cap = raw_snapshot.market_data.get('market_cap') if raw_snapshot.market_data else None

            screened_stocks.append(ScreenedStock(
                ticker=ticker,
                name=ticker_entry.name,
                overall_score=overall_score,
                total_points=total_points,
                max_points=max_score,
                scores=scores,
                price=price,
                market_cap=market_cap
            ))

        except Exception as e:
            # Skip stocks with errors
            continue

    # Sort by overall score (descending)
    screened_stocks.sort(key=lambda x: x.overall_score, reverse=True)

    return ScreenerResponse(
        stocks=screened_stocks,
        screened_at=datetime.now().isoformat(),
        criteria_count=len(screened_stocks[0].scores) if screened_stocks else 21
    )
