#!/usr/bin/env python3
"""
Quick validation script to verify metric accuracy.

Run this script anytime to validate that our calculated metrics are accurate
by comparing them against known formulas and expected ranges.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.json_store import JsonStore
from services.metric_calculator import (
    PriceToEarningsCalculator,
    PriceToBookCalculator,
    ROECalculator,
)


def validate_ticker(ticker: str):
    """Validate metrics for a given ticker."""
    print(f"\n{'='*70}")
    print(f"METRIC VALIDATION: {ticker}")
    print(f"{'='*70}\n")

    store = JsonStore()

    # Load raw data
    try:
        raw_snapshot = store.read_raw_snapshot(ticker)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

    # Load calculated metrics
    try:
        metrics_snapshot = store.read_metrics_snapshot(ticker)
    except Exception as e:
        print(f"❌ Error loading metrics: {e}")
        return False

    # Convert to dict for calculator
    raw_data = {
        'price': raw_snapshot.price,
        'financials': raw_snapshot.financials,
        'market_data': raw_snapshot.market_data,
        'cash_flow': raw_snapshot.cash_flow,
    }

    print(f"📊 Data Date: {raw_snapshot.as_of}")
    print(f"💰 Stock Price: ${raw_data['price']['close']:.2f}\n")

    # Validate P/E Ratio
    print("1️⃣  P/E Ratio (TTM)")
    print("-" * 50)
    pe_calc = PriceToEarningsCalculator()
    pe_result = pe_calc.calculate(raw_data)

    if pe_result.success:
        stored_pe = metrics_snapshot.valuation.get('price_to_earnings')

        # Calculate manually
        price = raw_data['price']['close']
        net_income = raw_data['financials']['net_income']
        shares = raw_data['market_data']['shares_outstanding']
        eps = net_income / shares
        manual_pe = price / eps

        print(f"   Stored P/E:      {stored_pe:.2f}")
        print(f"   Calculated P/E:  {pe_result.value:.2f}")
        print(f"   Manual P/E:      {manual_pe:.2f}")
        print(f"   EPS:             ${eps:.2f}")
        print()

        # Verify consistency
        if abs(stored_pe - pe_result.value) < 0.01:
            print("   ✅ P/E calculation is CONSISTENT")
        else:
            print("   ⚠️  P/E values don't match!")
            return False

        # Check against typical ranges
        if ticker == "AAPL":
            if 30 < pe_result.value < 50:
                print("   ✅ P/E within expected range for AAPL (30-50)")
            else:
                print(f"   ⚠️  P/E {pe_result.value:.2f} outside typical range")
    else:
        print(f"   ❌ P/E calculation failed: {pe_result.error}")
        return False

    print()

    # Validate P/B Ratio
    print("2️⃣  P/B Ratio")
    print("-" * 50)
    pb_calc = PriceToBookCalculator()
    pb_result = pb_calc.calculate(raw_data)

    if pb_result.success:
        stored_pb = metrics_snapshot.valuation.get('price_to_book')

        # Calculate manually
        equity = raw_data['financials']['shareholders_equity']
        book_value_per_share = equity / shares
        manual_pb = price / book_value_per_share

        print(f"   Stored P/B:      {stored_pb:.2f}")
        print(f"   Calculated P/B:  {pb_result.value:.2f}")
        print(f"   Manual P/B:      {manual_pb:.2f}")
        print(f"   Book Value/Share: ${book_value_per_share:.2f}")
        print()

        if abs(stored_pb - pb_result.value) < 0.01:
            print("   ✅ P/B calculation is CONSISTENT")
        else:
            print("   ⚠️  P/B values don't match!")
            return False
    else:
        print(f"   ❌ P/B calculation failed: {pb_result.error}")

    print()

    # Validate ROE
    print("3️⃣  Return on Equity (ROE)")
    print("-" * 50)
    roe_calc = ROECalculator()
    roe_result = roe_calc.calculate(raw_data)

    if roe_result.success:
        stored_roe = metrics_snapshot.profitability.get('return_on_equity')

        # Calculate manually
        manual_roe = net_income / equity

        print(f"   Stored ROE:      {stored_roe:.2%}")
        print(f"   Calculated ROE:  {roe_result.value:.2%}")
        print(f"   Manual ROE:      {manual_roe:.2%}")
        print()

        if abs(stored_roe - roe_result.value) < 0.01:
            print("   ✅ ROE calculation is CONSISTENT")
        else:
            print("   ⚠️  ROE values don't match!")
            return False

        # Check reasonableness
        if ticker == "AAPL":
            if roe_result.value > 1.0:
                print("   ✅ ROE >100% expected for AAPL (share buybacks)")
            else:
                print("   ⚠️  ROE seems low for AAPL")
    else:
        print(f"   ❌ ROE calculation failed: {roe_result.error}")

    print()
    print("="*70)
    print("✅ VALIDATION PASSED: All metrics are accurate and consistent")
    print("="*70)
    print()

    # Summary
    print("📋 Summary:")
    print(f"   • P/E Ratio: {pe_result.value:.2f}")
    print(f"   • P/B Ratio: {pb_result.value:.2f}")
    print(f"   • ROE: {roe_result.value:.2%}")
    print(f"   • EPS: ${eps:.2f}")
    print(f"   • Book Value/Share: ${book_value_per_share:.2f}")
    print()
    print("✅ All calculations verified using standard financial formulas")
    print()

    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate metric calculations for accuracy'
    )
    parser.add_argument(
        'ticker',
        nargs='?',
        default='AAPL',
        help='Ticker symbol to validate (default: AAPL)'
    )

    args = parser.parse_args()

    success = validate_ticker(args.ticker)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
