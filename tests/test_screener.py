"""
Tests for the Buffett/Munger stock screener scoring logic.

Validates that the screener correctly scores stocks against
all 21 value investing criteria and produces accurate pass/fail results.
"""

import pytest
from backend.api.routes.screener import score_metric


class TestScoreMetric:
    """Test the score_metric helper function."""

    def test_none_value(self):
        """None values should score 0 and fail."""
        score, passes = score_metric(None, target_min=0.15)
        assert score == 0.0
        assert not passes

    def test_normal_metric_passes(self):
        """Value above target_min should pass."""
        score, passes = score_metric(0.25, target_min=0.15)
        assert passes
        assert score == 1.0  # capped at 1.0

    def test_normal_metric_fails(self):
        """Value below target_min should fail with partial score."""
        score, passes = score_metric(0.10, target_min=0.15)
        assert not passes
        assert score == pytest.approx(0.667, rel=0.01)  # 0.10 / 0.15

    def test_inverse_metric_passes(self):
        """Value below target_max should pass for inverse metrics."""
        score, passes = score_metric(15.0, target_max=20.0, inverse=True)
        assert passes

    def test_inverse_metric_fails(self):
        """Value above target_max should fail for inverse metrics."""
        score, passes = score_metric(30.0, target_max=20.0, inverse=True)
        assert not passes
        assert score == pytest.approx(0.667, rel=0.01)  # 20/30

    def test_inverse_very_low_value(self):
        """Very low value for inverse metric should cap at 1.0."""
        score, passes = score_metric(0.5, target_max=20.0, inverse=True)
        assert passes
        assert score == 1.0  # Capped

    def test_zero_value_inverse(self):
        """Zero value for inverse metric should handle division safely."""
        score, passes = score_metric(0.0, target_max=20.0, inverse=True)
        assert passes
        assert score == 1.0  # target_max / max(0.0, 0.01) capped


class TestScreenerCriteria:
    """Verify all 21 screening criteria with a mock stock."""

    def test_perfect_buffett_stock(self):
        """A stock that passes ALL 21 Buffett/Munger criteria."""
        from backend.api.routes.screener import score_metric

        # Simulate a "perfect" Buffett stock
        criteria = [
            # (value, target_min, target_max, inverse, expected_pass)
            # Core criteria
            (12.0, None, 20, True, True),     # 1. P/E < 20
            (1.5, None, 3.0, True, True),     # 2. P/B < 3.0
            (0.8, None, 1.0, True, True),     # 3. PEG < 1.0
            (0.20, 0.15, None, False, True),  # 4. ROE > 15%
            (0.3, None, 0.5, True, True),     # 5. D/E < 0.5
            (2.0, 1.5, None, False, True),    # 6. Current Ratio > 1.5
            # (Earnings Stability and Dividend History have special scoring)
            (0.15, 0.10, None, False, True),  # 9. Operating Margin > 10%
            # (Piotroski has special scoring)

            # Buffett/Munger criteria
            (0.45, 0.40, None, False, True),  # 11. Gross Profit Margin > 40%
            (12.0, None, 15.0, True, True),   # 12. Price to FCF < 15
            (0.07, 0.05, None, False, True),  # 13. FCF Yield > 5%
            (1.3, 1.0, None, False, True),    # 14. Quality of Earnings > 1.0
            (0.20, 0.15, None, False, True),  # 15. CROIC > 15%
            (4.0, 3.0, None, False, True),    # 16. Z-Score > 3.0
            (2.0, None, 3.0, True, True),     # 17. Debt/EBITDA < 3.0
            (3.0, None, 4.0, True, True),     # 18. LT Debt/Earnings < 4
            (0.60, None, 0.80, True, True),   # 19. SG&A/GP < 80%
            (0.20, 0.15, None, False, True),  # 20. ROTE > 15%
            (0.15, 0.01, None, False, True),  # 21. Graham MoS > 0% (use 0.01 to avoid div-by-zero)
        ]

        all_pass = True
        for i, (value, target_min, target_max, inverse, expected_pass) in enumerate(criteria):
            score, passes = score_metric(value, target_min=target_min, target_max=target_max, inverse=inverse)
            if passes != expected_pass:
                all_pass = False
                print(f"  Criteria {i+1}: Expected {'pass' if expected_pass else 'fail'}, got {'pass' if passes else 'fail'}")

        assert all_pass, "Not all criteria scored correctly for perfect stock"

    def test_failing_buffett_stock(self):
        """A stock that fails key Buffett criteria (overleveraged, low margins)."""
        # High P/E = fail
        score, passes = score_metric(50.0, target_max=20, inverse=True)
        assert not passes

        # Low gross margin = fail
        score, passes = score_metric(0.15, target_min=0.40)
        assert not passes

        # High Debt/EBITDA = fail
        score, passes = score_metric(6.0, target_max=3.0, inverse=True)
        assert not passes

        # Low Z-Score = fail
        score, passes = score_metric(1.5, target_min=3.0)
        assert not passes

        # Negative earnings quality = fail
        score, passes = score_metric(0.5, target_min=1.0)
        assert not passes

    def test_criteria_count_is_21(self):
        """Verify the screener evaluates exactly 21 criteria."""
        # This tests the screener docstring claim
        from backend.api.routes.screener import get_value_screener
        import inspect

        source = inspect.getsource(get_value_screener)
        # Count ScreenerScore appends
        score_count = source.count("scores.append(ScreenerScore(")
        assert score_count == 21, (
            f"Expected 21 criteria in screener, found {score_count}"
        )


class TestScreenerScoreInterpretation:
    """Test that scores are interpretable and meaningful."""

    def test_score_range_normal(self):
        """Normal metric scores should be between 0 and 1."""
        for value in [0.0, 0.05, 0.10, 0.15, 0.20, 0.50, 1.0]:
            score, _ = score_metric(value, target_min=0.15)
            assert 0.0 <= score <= 1.0, f"Score {score} out of range for value {value}"

    def test_score_range_inverse(self):
        """Inverse metric scores should be between 0 and 1."""
        for value in [1.0, 5.0, 10.0, 20.0, 30.0, 100.0]:
            score, _ = score_metric(value, target_max=20.0, inverse=True)
            assert 0.0 <= score <= 1.0, f"Score {score} out of range for value {value}"

    def test_better_values_score_higher(self):
        """Higher values for normal metrics should score higher."""
        score_low, _ = score_metric(0.05, target_min=0.15)
        score_med, _ = score_metric(0.10, target_min=0.15)
        score_high, _ = score_metric(0.20, target_min=0.15)

        assert score_low < score_med < score_high

    def test_better_values_score_higher_inverse(self):
        """Lower values for inverse metrics should score higher."""
        score_high_val, _ = score_metric(50.0, target_max=20.0, inverse=True)
        score_med_val, _ = score_metric(25.0, target_max=20.0, inverse=True)
        score_low_val, _ = score_metric(10.0, target_max=20.0, inverse=True)

        assert score_high_val < score_med_val < score_low_val


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
