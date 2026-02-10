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
    # New Buffett/Munger calculators
    GrossProfitMarginCalculator,
    PriceToFCFCalculator,
    FCFYieldCalculator,
    LongTermDebtToEarningsCalculator,
    QualityOfEarningsCalculator,
    AltmanZScoreCalculator,
    CashConversionCycleCalculator,
    GrahamNumberCalculator,
    CROICCalculator,
    GrossMarginStabilityCalculator,
    DebtToEBITDACalculator,
    NetDebtToEquityCalculator,
    AccrualsRatioCalculator,
    AssetTurnoverCalculator,
    SustainableGrowthRateCalculator,
    CapExToDepreciationCalculator,
    SloanRatioCalculator,
    RDToRevenueCalculator,
    SGAToGrossProfitCalculator,
    GoodwillToAssetsCalculator,
    ReturnOnTangibleEquityCalculator,
    get_all_calculators,
)


@pytest.fixture
def sample_raw_data():
    """Sample raw data for testing all calculators."""
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
            'current_assets': 60000000,
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
            'net_margin': 0.20,
            # New fields for Buffett/Munger metrics
            'accounts_receivable': 12000000,
            'inventory': 8000000,
            'accounts_payable': 10000000,
            'goodwill': 15000000,
            'intangible_assets': 5000000,
            'research_and_development': 10000000,
            'selling_general_admin': 30000000,
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

        # Should have all 46 calculators (20 original + 26 Buffett/Munger)
        assert len(calculators) >= 46

        # Check that all expected metric IDs are present
        metric_ids = [calc.metric_id for calc in calculators]
        expected_ids = [
            # Original 20
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
            'consistency_score',
            # Buffett/Munger additions
            'gross_profit_margin',
            'price_to_fcf',
            'fcf_yield',
            'long_term_debt_to_earnings',
            'quality_of_earnings',
            'altman_z_score',
            'cash_conversion_cycle',
            'graham_number',
            'cash_return_on_invested_capital',
            'gross_margin_stability',
            'debt_to_ebitda',
            'net_debt_to_equity',
            'accruals_ratio',
            'asset_turnover',
            'sustainable_growth_rate',
            'capex_to_depreciation',
            'sloan_ratio',
            'rd_to_revenue',
            'sga_to_gross_profit',
            'goodwill_to_assets',
            'return_on_tangible_equity',
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


class TestBuffettMungerProfitability:
    """Test Buffett/Munger profitability metrics."""

    def test_gross_profit_margin(self, sample_raw_data):
        calc = GrossProfitMarginCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 60M / 100M = 0.60
        assert result.value == 0.60
        assert result.metadata['gross_profit'] == 60000000
        assert result.metadata['revenue'] == 100000000

    def test_gross_profit_margin_missing_data(self):
        calc = GrossProfitMarginCalculator()
        result = calc.calculate({'financials': {}})
        assert not result.success

    def test_quality_of_earnings(self, sample_raw_data):
        calc = QualityOfEarningsCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 30M / 20M = 1.5
        assert result.value == 1.5
        assert result.metadata['operating_cash_flow'] == 30000000
        assert result.metadata['net_income'] == 20000000

    def test_quality_of_earnings_low(self):
        """Company with poor earnings quality (more profit than cash)."""
        data = {
            'financials': {
                'operating_cash_flow': 5000000,
                'net_income': 20000000,
            }
        }
        calc = QualityOfEarningsCalculator()
        result = calc.calculate(data)

        assert result.success
        assert result.value == 0.25  # 5M / 20M
        assert result.value < 1.0  # Poor quality

    def test_croic(self, sample_raw_data):
        calc = CROICCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # FCF = 30M - 5M = 25M
        # Invested Capital = 50M + 80M - 15M = 115M
        # CROIC = 25M / 115M ≈ 0.2174
        assert result.value == pytest.approx(0.2174, rel=0.01)

    def test_asset_turnover(self, sample_raw_data):
        calc = AssetTurnoverCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 100M / 200M = 0.5
        assert result.value == 0.5

    def test_return_on_tangible_equity(self, sample_raw_data):
        calc = ReturnOnTangibleEquityCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # Tangible equity = 80M - 15M (goodwill) - 5M (intangibles) = 60M
        # ROTE = 20M / 60M = 0.3333
        assert result.value == pytest.approx(0.3333, rel=0.01)

    def test_return_on_tangible_equity_negative_tangible(self):
        """Test when goodwill exceeds equity (should fail gracefully)."""
        data = {
            'financials': {
                'net_income': 20000000,
                'shareholders_equity': 30000000,
                'goodwill': 25000000,
                'intangible_assets': 10000000,
            }
        }
        calc = ReturnOnTangibleEquityCalculator()
        result = calc.calculate(data)
        # tangible_equity = 30M - 25M - 10M = -5M (negative)
        assert not result.success

    def test_accruals_ratio(self, sample_raw_data):
        calc = AccrualsRatioCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # (20M - 30M) / 200M = -0.05
        assert result.value == pytest.approx(-0.05, rel=0.01)
        # Negative accruals ratio = good quality

    def test_sloan_ratio(self, sample_raw_data):
        calc = SloanRatioCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # (20M - (30M - 5M)) / 200M = (20M - 25M) / 200M = -0.025
        assert result.value == pytest.approx(-0.025, rel=0.01)

    def test_sustainable_growth_rate(self, sample_raw_data):
        calc = SustainableGrowthRateCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # ROE = 20M / 80M = 0.25
        # retention = 1 - (5M / 20M) = 0.75
        # SGR = 0.25 * 0.75 = 0.1875
        assert result.value == pytest.approx(0.1875, rel=0.01)


class TestBuffettMungerValuation:
    """Test Buffett/Munger valuation metrics."""

    def test_price_to_fcf(self, sample_raw_data):
        calc = PriceToFCFCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # FCF = 30M - 5M = 25M
        # P/FCF = 3000M / 25M = 120
        assert result.value == pytest.approx(120.0, rel=0.01)

    def test_fcf_yield(self, sample_raw_data):
        calc = FCFYieldCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # FCF = 25M, Market Cap = 3000M
        # FCF Yield = 25M / 3000M ≈ 0.00833
        assert result.value == pytest.approx(0.00833, rel=0.01)

    def test_graham_number(self, sample_raw_data):
        calc = GrahamNumberCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        assert isinstance(result.value, dict)
        assert 'graham_number' in result.value
        assert 'current_price' in result.value
        assert 'margin_of_safety' in result.value

        # EPS = 20M / 20M = 1.0
        # BVPS = 80M / 20M = 4.0
        # Graham = sqrt(22.5 * 1.0 * 4.0) = sqrt(90) ≈ 9.49
        import math
        expected_graham = math.sqrt(22.5 * 1.0 * 4.0)
        assert result.value['graham_number'] == pytest.approx(expected_graham, rel=0.01)
        assert result.value['current_price'] == 150.0
        # Stock is overvalued (150 >> 9.49)
        assert result.value['margin_of_safety'] < 0

        # Verify metadata
        assert result.metadata['eps'] == 1.0
        assert result.metadata['bvps'] == 4.0


class TestBuffettMungerFinancialStrength:
    """Test Buffett/Munger financial strength metrics."""

    def test_altman_z_score(self, sample_raw_data):
        calc = AltmanZScoreCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # X1 = (60M - 40M) / 200M = 0.10
        # X2 = 50M / 200M = 0.25
        # X3 = 25M / 200M = 0.125
        # X4 = 3000M / 120M = 25.0
        # X5 = 100M / 200M = 0.5
        # Z = 1.2*0.10 + 1.4*0.25 + 3.3*0.125 + 0.6*25.0 + 1.0*0.5
        # Z = 0.12 + 0.35 + 0.4125 + 15.0 + 0.5 = 16.38
        assert result.value > 3.0  # Safe zone
        assert 'working_capital_ratio' in result.metadata
        assert 'risk' in result.metadata
        assert result.metadata['risk'] == 'safe'

    def test_altman_z_score_distress(self):
        """Test company in distress zone."""
        data = {
            'financials': {
                'current_assets': 20000000,
                'current_liabilities': 40000000,
                'total_assets': 200000000,
                'total_liabilities': 180000000,
                'retained_earnings': -10000000,
                'ebit': 5000000,
                'revenue': 50000000,
            },
            'market_data': {'market_cap': 30000000}
        }
        calc = AltmanZScoreCalculator()
        result = calc.calculate(data)

        assert result.success
        assert result.value < 1.8  # Distress zone
        assert result.metadata['risk'] == 'distress'

    def test_debt_to_ebitda(self, sample_raw_data):
        calc = DebtToEBITDACalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 50M / 28M ≈ 1.786
        assert result.value == pytest.approx(1.786, rel=0.01)

    def test_long_term_debt_to_earnings(self, sample_raw_data):
        calc = LongTermDebtToEarningsCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 50M / 20M = 2.5 years
        assert result.value == 2.5

    def test_long_term_debt_to_earnings_negative_income(self):
        """Should fail when net income is negative."""
        data = {
            'financials': {
                'total_debt': 50000000,
                'net_income': -10000000,
            }
        }
        calc = LongTermDebtToEarningsCalculator()
        result = calc.calculate(data)
        assert not result.success

    def test_net_debt_to_equity(self, sample_raw_data):
        calc = NetDebtToEquityCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # (50M - 15M) / 80M = 0.4375
        assert result.value == pytest.approx(0.4375, rel=0.01)

    def test_net_debt_to_equity_cash_rich(self):
        """Company with more cash than debt (negative net debt)."""
        data = {
            'financials': {
                'total_debt': 10000000,
                'cash_and_equivalents': 50000000,
                'shareholders_equity': 80000000,
            }
        }
        calc = NetDebtToEquityCalculator()
        result = calc.calculate(data)

        assert result.success
        # (10M - 50M) / 80M = -0.5 (negative = more cash than debt)
        assert result.value == pytest.approx(-0.5, rel=0.01)
        assert result.value < 0  # Cash-rich company


class TestBuffettMungerEfficiency:
    """Test Buffett/Munger efficiency and SEC EDGAR-sourced metrics."""

    def test_cash_conversion_cycle(self, sample_raw_data):
        calc = CashConversionCycleCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # DSO = (12M / 100M) * 365 = 43.8 days
        # DIO = (8M / 40M) * 365 = 73.0 days  (COGS = Revenue - Gross Profit = 40M)
        # DPO = (10M / 40M) * 365 = 91.25 days
        # CCC = 43.8 + 73.0 - 91.25 = 25.55 days
        assert result.value == pytest.approx(25.55, rel=0.01)
        assert result.metadata['dso'] == pytest.approx(43.8, rel=0.01)
        assert result.metadata['dio'] == pytest.approx(73.0, rel=0.01)
        assert result.metadata['dpo'] == pytest.approx(91.25, rel=0.01)

    def test_capex_to_depreciation(self, sample_raw_data):
        calc = CapExToDepreciationCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # |5M| / 3M ≈ 1.667
        assert result.value == pytest.approx(1.667, rel=0.01)

    def test_rd_to_revenue(self, sample_raw_data):
        calc = RDToRevenueCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 10M / 100M = 0.10
        assert result.value == 0.10

    def test_rd_to_revenue_no_rd(self):
        """Companies without R&D should fail gracefully."""
        data = {
            'financials': {
                'revenue': 100000000,
            }
        }
        calc = RDToRevenueCalculator()
        result = calc.calculate(data)
        assert not result.success

    def test_sga_to_gross_profit(self, sample_raw_data):
        calc = SGAToGrossProfitCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 30M / 60M = 0.50
        assert result.value == 0.50
        # Below 80% = efficient (Munger's threshold)
        assert result.value < 0.80

    def test_goodwill_to_assets(self, sample_raw_data):
        calc = GoodwillToAssetsCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # 15M / 200M = 0.075
        assert result.value == 0.075

    def test_gross_margin_stability(self, sample_raw_data):
        calc = GrossMarginStabilityCalculator()
        result = calc.calculate(sample_raw_data)

        assert result.success
        # History has gross margins: 0.57, 0.58, 0.59, 0.60 (current)
        # Very stable margins - value is the stability score (1 - coefficient_of_variation)
        assert result.value > 0.9  # High stability
        assert result.metadata['stability'] == 'very_stable'
        assert result.metadata['years_analyzed'] >= 3


class TestBuffettMungerEdgeCases:
    """Test edge cases and boundary conditions for new calculators."""

    def test_zero_revenue_gross_margin(self):
        data = {'financials': {'gross_profit': 10000000, 'revenue': 0}}
        calc = GrossProfitMarginCalculator()
        result = calc.calculate(data)
        assert not result.success

    def test_zero_market_cap_fcf_yield(self):
        data = {
            'financials': {'operating_cash_flow': 30000000, 'capital_expenditure': -5000000},
            'market_data': {'market_cap': 0}
        }
        calc = FCFYieldCalculator()
        result = calc.calculate(data)
        assert not result.success

    def test_zero_ebitda_debt_ratio(self):
        data = {'financials': {'total_debt': 50000000, 'ebitda': 0}}
        calc = DebtToEBITDACalculator()
        result = calc.calculate(data)
        assert not result.success

    def test_zero_equity_net_debt(self):
        data = {
            'financials': {
                'total_debt': 50000000,
                'cash_and_equivalents': 15000000,
                'shareholders_equity': 0,
            }
        }
        calc = NetDebtToEquityCalculator()
        result = calc.calculate(data)
        assert not result.success

    def test_graham_number_negative_eps(self):
        """Graham number should fail with negative earnings."""
        data = {
            'financials': {
                'net_income': -10000000,
                'shareholders_equity': 80000000,
            },
            'market_data': {'shares_outstanding': 20000000},
            'price': {'close': 50.0}
        }
        calc = GrahamNumberCalculator()
        result = calc.calculate(data)
        assert not result.success

    def test_all_calculators_handle_empty_data(self):
        """Every calculator should handle empty data gracefully without crashing."""
        empty_data = {'ticker': 'EMPTY', 'financials': {}, 'market_data': {}}
        calculators = get_all_calculators()

        for calc in calculators:
            result = calc.calculate(empty_data)
            # Must not crash; should fail gracefully
            assert result is not None, f"{calc.metric_id} returned None"
            assert not result.success or result.value is not None, (
                f"{calc.metric_id} claims success but has no value"
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
