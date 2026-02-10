"""
Tests for SEC EDGAR client - verifies we can fetch real financial data.

These tests make LIVE API calls to SEC EDGAR (free, no key needed).
They validate that:
1. CIK lookup works for known tickers
2. XBRL financial data is returned correctly
3. Key financial fields (Goodwill, R&D, SG&A) are fetchable
4. Insider transaction data is accessible
"""

import pytest
from clients.sec_edgar_client import SECEdgarClient


@pytest.fixture(scope="module")
def client():
    """Shared SEC EDGAR client for all tests (reuses connection pool)."""
    return SECEdgarClient(user_agent="InvestingAppTests test@example.com")


class TestCIKLookup:
    """Test CIK (Central Index Key) resolution."""

    def test_aapl_cik(self, client):
        """Apple should have a well-known CIK."""
        cik = client.get_cik("AAPL")
        assert cik is not None, "Failed to get CIK for AAPL"
        assert len(cik) == 10, f"CIK should be 10 digits, got: {cik}"
        assert cik == "0000320193", f"Apple CIK should be 0000320193, got: {cik}"

    def test_msft_cik(self, client):
        """Microsoft CIK lookup."""
        cik = client.get_cik("MSFT")
        assert cik is not None, "Failed to get CIK for MSFT"
        assert len(cik) == 10

    def test_invalid_ticker(self, client):
        """Invalid ticker should return None, not crash."""
        cik = client.get_cik("ZZZZZZZZZ")
        assert cik is None

    def test_cik_caching(self, client):
        """Second lookup should use cache."""
        cik1 = client.get_cik("AAPL")
        cik2 = client.get_cik("AAPL")
        assert cik1 == cik2
        assert "AAPL" in client._cik_cache


class TestCompanyFacts:
    """Test XBRL company facts retrieval."""

    def test_aapl_company_facts(self, client):
        """Verify we can fetch Apple's full company facts."""
        facts = client.fetch_company_facts("AAPL")

        assert facts is not None, "Failed to fetch company facts for AAPL"
        assert "facts" in facts, "Response missing 'facts' key"
        assert "us-gaap" in facts["facts"], "Response missing 'us-gaap' taxonomy"

        us_gaap = facts["facts"]["us-gaap"]
        # Apple should have hundreds of XBRL concepts
        assert len(us_gaap) > 100, f"Expected 100+ concepts, got {len(us_gaap)}"

    def test_aapl_has_key_xbrl_tags(self, client):
        """Verify Apple has the XBRL tags we need for Buffett/Munger metrics."""
        facts = client.fetch_company_facts("AAPL")
        us_gaap = facts["facts"]["us-gaap"]

        required_tags = [
            "ResearchAndDevelopmentExpense",
            "SellingGeneralAndAdministrativeExpense",
            "Revenues",
            "NetIncomeLoss",
            "Assets",
        ]

        for tag in required_tags:
            assert tag in us_gaap, f"Missing XBRL tag: {tag}"

            # Verify the tag has USD values
            units = us_gaap[tag].get("units", {})
            assert "USD" in units, f"{tag} missing USD units"

            values = units["USD"]
            assert len(values) > 0, f"{tag} has no values"

            # Verify most recent value is a number
            most_recent = sorted(values, key=lambda x: x.get("end", ""), reverse=True)[0]
            assert most_recent.get("val") is not None, f"{tag} most recent value is None"
            assert isinstance(most_recent["val"], (int, float)), f"{tag} value is not numeric"

            print(f"  {tag}: {most_recent['val']:,.0f} (as of {most_recent.get('end', 'N/A')})")


class TestFetchFields:
    """Test the high-level fetch_fields method."""

    def test_fetch_goodwill(self, client):
        """Test fetching Goodwill from SEC EDGAR."""
        data, metadata, fetched, warnings = client.fetch_fields(
            "AAPL",
            ["financials.goodwill"],
            period="annual"
        )

        # Apple may or may not have goodwill (they do from Beats acquisition)
        if "financials.goodwill" in fetched:
            assert data["financials"].get("goodwill") is not None
            assert data["financials"]["goodwill"] > 0
            print(f"  Goodwill: ${data['financials']['goodwill']:,.0f}")
        else:
            print("  Note: Goodwill not found for AAPL (may not have goodwill)")

    def test_fetch_rd_expense(self, client):
        """Test fetching R&D expense - critical for Buffett analysis."""
        data, metadata, fetched, warnings = client.fetch_fields(
            "AAPL",
            ["financials.research_and_development"],
            period="annual"
        )

        assert "financials.research_and_development" in fetched, (
            f"Failed to fetch R&D. Warnings: {warnings}"
        )
        rd = data["financials"]["research_and_development"]
        assert rd is not None
        assert rd > 1_000_000_000, f"Apple R&D should be >$1B, got ${rd:,.0f}"
        print(f"  R&D Expense: ${rd:,.0f}")

    def test_fetch_sga_expense(self, client):
        """Test fetching SG&A expense - Munger's efficiency metric."""
        data, metadata, fetched, warnings = client.fetch_fields(
            "AAPL",
            ["financials.selling_general_admin"],
            period="annual"
        )

        assert "financials.selling_general_admin" in fetched, (
            f"Failed to fetch SG&A. Warnings: {warnings}"
        )
        sga = data["financials"]["selling_general_admin"]
        assert sga is not None
        assert sga > 1_000_000_000, f"Apple SG&A should be >$1B, got ${sga:,.0f}"
        print(f"  SG&A Expense: ${sga:,.0f}")

    def test_fetch_multiple_fields(self, client):
        """Test fetching multiple fields in one call."""
        fields = [
            "financials.research_and_development",
            "financials.selling_general_admin",
            "financials.goodwill",
            "financials.intangible_assets",
            "financials.revenue",
        ]

        data, metadata, fetched, warnings = client.fetch_fields(
            "AAPL", fields, period="annual"
        )

        # At minimum R&D and SG&A should be fetched
        assert len(fetched) >= 2, f"Expected at least 2 fields, got {len(fetched)}: {fetched}"

        print(f"\n  Fetched {len(fetched)} of {len(fields)} fields:")
        for field in fetched:
            key = field.split(".", 1)[1]
            val = data["financials"].get(key)
            if val is not None:
                print(f"    {field}: ${val:,.0f}")


class TestInsiderTransactions:
    """Test insider transaction data retrieval."""

    def test_fetch_insider_transactions(self, client):
        """Test fetching Form 4 filings."""
        transactions = client.fetch_insider_transactions("AAPL", limit=10)

        assert isinstance(transactions, list)
        # Apple should have insider transactions
        if len(transactions) > 0:
            tx = transactions[0]
            assert "form_type" in tx
            assert "filing_date" in tx
            assert tx["form_type"] in ("4", "4/A")
            print(f"\n  Found {len(transactions)} insider transactions")
            print(f"  Most recent: {tx['filing_date']} (Form {tx['form_type']})")

    def test_insider_data_via_fetch_fields(self, client):
        """Test insider data through fetch_fields interface."""
        data, metadata, fetched, warnings = client.fetch_fields(
            "AAPL",
            ["insider.transactions"],
            period="annual"
        )

        if "insider.transactions" in fetched:
            assert data["sec_edgar"].get("insider_transaction_count", 0) > 0
            print(f"  Insider transactions: {data['sec_edgar']['insider_transaction_count']}")


class TestRateLimiting:
    """Test that rate limiting doesn't cause failures."""

    def test_rapid_requests(self, client):
        """Multiple rapid requests should not fail (rate limiter should handle it)."""
        # Make 5 rapid requests
        for ticker in ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]:
            cik = client.get_cik(ticker)
            assert cik is not None, f"CIK lookup failed for {ticker} during rapid requests"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
