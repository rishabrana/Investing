"""
Comprehensive tests for all metric calculators.
"""

import pytest
from services.metric_calculator import (
    FreeCashFlowCalculator,
    ROICCalculator,
    ROECalculator,
    OperatingMarginsCalculator,
    OwnerEarningsCalculator,
    DebtToEquityCalculator,
    CapexRatioCalculator,
    PriceToEarningsCalculator,
    PriceToBookCalculator,
    EVToEBITDACalculator,
    DividendMetricsCalculator,
    MarginOfSafetyCalculator,
    PEGRatioCalculator,
    EPSGrowthCalculator,
    BookValuePerShareGrowthCalculator,
    ReturnOnRetainedEarningsCalculator,
    WACCvsROICSpreadCalculator,
    TenYearAverageROCECalculator,
    EconomicMoatScoreCalculator,
    ConsistencyScoreCalculator,
    get_all_calculators,
)


@pytest.fixture
def sample_raw_data():
    """Sample raw data for testing."""
    return {
        'ticker': 'TEST',
        'as_of': '2024-12-31',
        'price': {
            'close': 150.00
        },
        'financials': {
            'revenue': 100000000,
            'net_income': 20000000,
            'operating_income': 25000000,
            'gross_profit': 60000000,
            'ebit': 25000000,
            'shareholders_equity': 80000000,
            'total_assets': 200000000,
            'total_liabilities': 120000000,
            'current_liabilities': 40000000,
            'total_debt': 50000000,
            'operating_cash_flow': 30000000,
            'capital_expenditure': -5000000,
            'cash_and_equivalents': 15000000,
            'depreciation_amortization': 3000000,
            'ebitda': 28000000,
            'interest_expense': 2000000,
            'income_tax_expense': 5000000,
            'pre_tax_income': 25000000,
            'retained_earnings': 50000000,
            'gross_margin': 0.60,
            'operating_margin': 0.25,
            'net_margin': 0.20
        },
        'market_data': {
            'market_cap': 3000000000,
            'shares_outstanding': 20000000
        },
        'cash_flow': {
            'dividends_paid': -5000000
        },
        'assumptions': {
            'discount_rate': 0.10,
            'terminal_growth': 0.03,
            'projection_years': 5,
            'wacc': 0.08
        },
        'financials_history': [
            {
                'revenue': 70000000,
                'net_income': 12000000,
                'shareholders_equity': 65000000,
                'shares_outstanding': 20000000,
                'retained_earnings': 35000000,
                'ebit': 18000000,
                'total_assets': 170000000,
                'current_liabilities': 37000000,
                'gross_margin': 0.57,
                'operating_margin': 0.22
            },
            {
                'revenue': 80000000,
                'net_income': 15000000,
                'shareholders_equity': 70000000,
                'shares_outstanding': 20000000,
                'retained_earnings': 40000000,
                'ebit': 20000000,
                'total_assets': 180000000,
                'current_liabilities': 38000000,
                'gross_margin': 0.58,
                'operating_margin': 0.23
            },
            {
                'revenue': 90000000,
                'net_income': 17000000,
                'shareholders_equity': 75000000,
                'shares_outstanding': 20000000,
                'retained_earnings': 45000000,
                'ebit': 22000000,
                'total_assets': 190000000,
                'current_liabilities': 39000000,
                'gross_margin': 0.59,
                'operating_margin': 0.24
            }
        ],
        'market_data_history': [],
        'cash_flow_history': [
            {'free_cash_flow': 18000000},
            {'free_cash_flow': 20000000},
            {'free_cash_flow': 25000000}
        ],
        'metrics_history': [
            {'roic': 0.10, 'roe': 0.16},
            {'roic': 0.12, 'roe': 0.18},
            {'roic': 0.14, 'roe': 0.20}
        ],
        'projections': {
            'projected_fcf': [30000000, 33000000, 36300000, 39930000, 43923000]
        }
    }


class TestBasicMetrics:
    """Test basic profitability and financial strength metrics."""

    def test_free_cash_flow(self, sample_raw_data):
        calc = FreeCashFlowCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value == 25000000  # 30M - 5M
        assert result.metadata['operating_cash_flow'] == 30000000
        assert result.metadata['capital_expenditure'] == -5000000

    def test_roic(self, sample_raw_data):
        calc = ROICCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value is not None
        assert 0 < result.value < 1  # Should be a reasonable percentage
        assert 'nopat' in result.metadata
        assert 'invested_capital' in result.metadata

    def test_roe(self, sample_raw_data):
        calc = ROECalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value == 0.25  # 20M / 80M
        assert result.metadata['net_income'] == 20000000
        assert result.metadata['shareholders_equity'] == 80000000

    def test_operating_margins(self, sample_raw_data):
        calc = OperatingMarginsCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value['operating_margin'] == 0.25
        assert result.value['net_margin'] == 0.20

    def test_owner_earnings(self, sample_raw_data):
        calc = OwnerEarningsCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 20M (net income) + 3M (D&A) - 5M (capex) = 18M
        assert result.value == 18000000

    def test_debt_to_equity(self, sample_raw_data):
        calc = DebtToEquityCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value['debt_to_equity'] == 1.5  # 120M / 80M
        assert result.value['interest_coverage'] == 12.5  # 25M / 2M

    def test_capex_ratio(self, sample_raw_data):
        calc = CapexRatioCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value == pytest.approx(0.1667, rel=0.01)  # 5M / 30M


class TestValuationMetrics:
    """Test valuation metrics."""

    def test_price_to_earnings(self, sample_raw_data):
        calc = PriceToEarningsCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        eps = 20000000 / 20000000  # 1.0
        assert result.value == 150.0  # price / eps
        assert result.metadata['eps'] == 1.0

    def test_price_to_book(self, sample_raw_data):
        calc = PriceToBookCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        bvps = 80000000 / 20000000  # 4.0
        assert result.value == 37.5  # 150 / 4.0
        assert result.metadata['book_value_per_share'] == 4.0

    def test_ev_to_ebitda(self, sample_raw_data):
        calc = EVToEBITDACalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # EV = 3000M + 50M - 15M = 3035M
        # EV/EBITDA = 3035M / 28M ≈ 108.39
        assert result.value == pytest.approx(108.39, rel=0.01)

    def test_margin_of_safety(self, sample_raw_data):
        calc = MarginOfSafetyCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value is not None
        assert 'intrinsic_value' in result.metadata
        assert 'market_price' in result.metadata

    def test_margin_of_safety_missing_data(self, sample_raw_data):
        data = sample_raw_data.copy()
        data['projections'] = {}

        calc = MarginOfSafetyCalculator()
        result = calc.calculate(data)

        assert not result.success
        assert 'Missing price or projected cash flows' in result.error

    def test_peg_ratio(self, sample_raw_data):
        calc = PEGRatioCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value is not None
        assert 'pe_ratio' in result.metadata
        assert 'eps_growth_rate' in result.metadata


class TestGrowthMetrics:
    """Test growth metrics."""

    def test_eps_growth(self, sample_raw_data):
        calc = EPSGrowthCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value > 0  # Should show positive growth
        assert 'eps_latest' in result.metadata
        assert 'eps_base' in result.metadata
        assert 'years' in result.metadata

    def test_eps_growth_insufficient_data(self, sample_raw_data):
        data = sample_raw_data.copy()
        data['financials_history'] = []

        calc = EPSGrowthCalculator()
        result = calc.calculate(data)

        assert not result.success
        assert 'Insufficient historical data' in result.error

    def test_book_value_per_share_growth(self, sample_raw_data):
        calc = BookValuePerShareGrowthCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value > 0  # Should show positive growth
        assert 'bvps_latest' in result.metadata
        assert 'bvps_base' in result.metadata


class TestCapitalAllocationMetrics:
    """Test capital allocation metrics."""

    def test_dividend_metrics(self, sample_raw_data):
        calc = DividendMetricsCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value['dividend_yield'] is not None
        assert result.value['payout_ratio'] == 0.25  # 5M / 20M

    def test_return_on_retained_earnings(self, sample_raw_data):
        calc = ReturnOnRetainedEarningsCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value is not None
        assert 'earnings_retained' in result.metadata
        assert 'value_created' in result.metadata

    def test_wacc_vs_roic_spread(self, sample_raw_data):
        calc = WACCvsROICSpreadCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value is not None
        assert 'roic' in result.metadata
        assert 'wacc' in result.metadata
        assert result.metadata['wacc'] == 0.08


class TestLongTermMetrics:
    """Test long-term performance metrics."""

    def test_ten_year_average_roce(self, sample_raw_data):
        calc = TenYearAverageROCECalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert result.value > 0
        assert 'years_included' in result.metadata
        assert 'roce_history' in result.metadata

    def test_ten_year_average_roce_insufficient_data(self, sample_raw_data):
        data = sample_raw_data.copy()
        data['financials_history'] = []

        calc = TenYearAverageROCECalculator()
        result = calc.calculate(data)

        assert not result.success
        assert 'Insufficient historical data' in result.error


class TestMoatMetrics:
    """Test economic moat metrics."""

    def test_economic_moat_score(self, sample_raw_data):
        calc = EconomicMoatScoreCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert 'score' in result.value
        assert 'label' in result.value
        assert result.value['label'] in ['wide', 'narrow', 'none']
        assert 0 <= result.value['score'] <= 1

    def test_economic_moat_score_insufficient_data(self, sample_raw_data):
        data = sample_raw_data.copy()
        data['financials_history'] = []

        calc = EconomicMoatScoreCalculator()
        result = calc.calculate(data)

        assert not result.success
        assert 'Need at least 3 years' in result.error

    def test_consistency_score(self, sample_raw_data):
        calc = ConsistencyScoreCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert 'score' in result.value
        assert 'label' in result.value
        assert result.value['label'] in ['highly_consistent', 'consistent', 'moderate', 'volatile']
        assert 0 <= result.value['score'] <= 1

    def test_consistency_score_insufficient_data(self, sample_raw_data):
        data = sample_raw_data.copy()
        data['financials_history'] = []

        calc = ConsistencyScoreCalculator()
        result = calc.calculate(data)

        assert not result.success
        assert 'Need at least 3 years' in result.error


class TestCalculatorRegistry:
    """Test calculator registry functions."""

    def test_get_all_calculators(self):
        calculators = get_all_calculators()

        # Should have all 20 calculators
        assert len(calculators) == 20

        # Check that all expected metric IDs are present
        metric_ids = [calc.metric_id for calc in calculators]
        expected_ids = [
            'free_cash_flow',
            'return_on_invested_capital',
            'return_on_equity',
            'operating_and_net_margin',
            'owner_earnings',
            'debt_to_equity_and_interest_coverage',
            'capital_expenditure_ratio',
            'price_to_earnings',
            'price_to_book',
            'ev_to_ebitda',
            'margin_of_safety',
            'peg_ratio',
            'eps_growth',
            'book_value_per_share_growth',
            'dividend_yield_and_payout_ratio',
            'return_on_retained_earnings',
            'wacc_vs_roic_spread',
            'ten_year_average_roce',
            'economic_moat_score',
            'consistency_score'
        ]

        for expected_id in expected_ids:
            assert expected_id in metric_ids, f"Missing calculator: {expected_id}"


class TestErrorHandling:
    """Test error handling in calculators."""

    def test_missing_required_fields(self):
        data = {'ticker': 'TEST'}

        calc = FreeCashFlowCalculator()
        result = calc.calculate(data)

        assert not result.success
        assert result.error is not None

    def test_zero_division_handling(self):
        data = {
            'financials': {
                'net_income': 1000000,
                'shareholders_equity': 0  # Zero equity
            }
        }

        calc = ROECalculator()
        result = calc.calculate(data)

        assert not result.success
        assert 'zero' in result.error.lower()

    def test_negative_values_in_growth(self, sample_raw_data):
        data = sample_raw_data.copy()
        # Set negative base EPS
        data['financials_history'][0]['net_income'] = -1000000

        calc = EPSGrowthCalculator()
        result = calc.calculate(data)

        assert not result.success
        assert 'negative' in result.error.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
