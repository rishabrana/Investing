"""SEC EDGAR API client for accessing free XBRL financial data and Form 4 filings."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Iterable, Optional, Set, Tuple

import requests


logger = logging.getLogger(__name__)


class SECEdgarClient:
    """
    SEC EDGAR API client for free access to:
    - XBRL financial data (Company Facts API)
    - Filing history and Form 4 insider transactions
    - Company concept data

    No API key required. Rate limit: 10 requests/second.
    Must include User-Agent header per SEC requirements.
    """

    BASE_URL = "https://data.sec.gov"
    SEC_SEARCH_URL = "https://www.sec.gov"

    # Common XBRL tags for financial data
    XBRL_TAGS = {
        # Balance Sheet - Additional items not in other APIs
        "goodwill": "Goodwill",
        "intangible_assets": "IntangibleAssetsNetExcludingGoodwill",
        "other_intangible_assets": "OtherIntangibleAssetsNet",
        "finite_lived_intangibles": "FiniteLivedIntangibleAssetsNet",
        "indefinite_lived_intangibles": "IndefiniteLivedIntangibleAssetsExcludingGoodwill",

        # Income Statement - Additional items
        "research_and_development": "ResearchAndDevelopmentExpense",
        "selling_general_admin": "SellingGeneralAndAdministrativeExpense",
        "cost_of_goods_sold": "CostOfGoodsAndServicesSold",
        "cost_of_revenue": "CostOfRevenue",

        # Standard fields (for fallback/verification)
        "revenue": "Revenues",
        "revenue_alt": "RevenueFromContractWithCustomerExcludingAssessedTax",
        "net_income": "NetIncomeLoss",
        "total_assets": "Assets",
        "total_liabilities": "Liabilities",
        "stockholders_equity": "StockholdersEquity",
        "shares_outstanding": "CommonStockSharesOutstanding",
        "shares_outstanding_alt": "WeightedAverageNumberOfSharesOutstandingBasic",
    }

    def __init__(
        self,
        user_agent: str = "InvestingApp contact@example.com",
        session: Optional[requests.Session] = None,
    ):
        """
        Initialize SEC EDGAR client.

        Args:
            user_agent: Required User-Agent string (SEC requires contact info).
                        Format: "AppName contact@email.com"
            session: Optional requests session for connection pooling.
        """
        self.user_agent = user_agent
        self.session = session or requests.Session()
        self._cik_cache: Dict[str, str] = {}
        self._ticker_directory: Optional[Dict[str, str]] = None  # ticker -> company name
        self._last_request_time = 0.0
        self._min_request_interval = 0.1  # 10 requests/second max

    # -------- public API --------

    def _load_ticker_directory(self) -> Dict[str, str]:
        """Load and cache the full SEC ticker directory (ticker -> company name)."""
        if self._ticker_directory is not None:
            return self._ticker_directory

        try:
            payload = self._make_request_url(
                f"{self.SEC_SEARCH_URL}/files/company_tickers.json"
            )
            self._ticker_directory = {}
            for entry in payload.values():
                t = entry.get("ticker", "")
                name = entry.get("title", t)
                if t:
                    self._ticker_directory[t.upper()] = name
                    # Also cache CIK while we have it
                    cik = str(entry.get("cik_str", "")).zfill(10)
                    self._cik_cache[t.upper()] = cik
            return self._ticker_directory
        except Exception as exc:
            logger.error(f"Failed to load ticker directory: {exc}")
            return {}

    def validate_ticker(self, ticker: str) -> Tuple[bool, str, str]:
        """
        Validate a ticker symbol using the SEC EDGAR company directory.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Tuple of (is_valid, company_name, error_message)
        """
        ticker = ticker.upper()
        directory = self._load_ticker_directory()
        if ticker in directory:
            return True, directory[ticker], ""
        return False, "", f"Ticker '{ticker}' not found in SEC EDGAR"

    def get_cik(self, ticker: str) -> Optional[str]:
        """
        Get CIK (Central Index Key) for a ticker symbol.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")

        Returns:
            10-digit CIK string or None if not found.
        """
        ticker = ticker.upper()

        if ticker in self._cik_cache:
            return self._cik_cache[ticker]

        # Loading the directory also populates _cik_cache
        self._load_ticker_directory()

        if ticker in self._cik_cache:
            return self._cik_cache[ticker]

        logger.warning(f"CIK not found for ticker: {ticker}")
        return None

    def fetch_company_facts(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch all XBRL company facts for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Full company facts JSON or None if failed.
        """
        cik = self.get_cik(ticker)
        if not cik:
            return None

        try:
            return self._make_request(f"/api/xbrl/companyfacts/CIK{cik}.json")
        except Exception as exc:
            logger.error(f"Failed to fetch company facts for {ticker}: {exc}")
            return None

    def fetch_fields(
        self,
        ticker: str,
        fields: Iterable[str],
        period: str = "annual",
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Set[str], list[str]]:
        """
        Fetch requested fields from SEC EDGAR XBRL data.

        Args:
            ticker: Stock ticker symbol
            fields: List of field identifiers to fetch
            period: "annual" or "quarterly"

        Returns:
            Tuple of (data, source_metadata, fetched_fields, warnings)
        """
        ticker = ticker.upper()
        requested = set(fields)
        data: Dict[str, Any] = {
            "price": {},
            "market_data": {},
            "financials": {},
            "cash_flow": {},
            "sec_edgar": {},  # SEC-specific data
        }
        source_metadata: Dict[str, Any] = {}
        fetched: Set[str] = set()
        warnings: list[str] = []

        # Fetch company facts (contains all XBRL data)
        company_facts = self.fetch_company_facts(ticker)
        if not company_facts:
            warnings.append(f"SEC EDGAR: Could not fetch company facts for {ticker}")
            return data, source_metadata, fetched, warnings

        us_gaap = company_facts.get("facts", {}).get("us-gaap", {})

        # Map requested fields to XBRL tags and extract data
        try:
            fetched |= self._extract_xbrl_data(
                us_gaap, requested, period, data, source_metadata
            )
        except Exception as exc:
            msg = f"SEC EDGAR XBRL extraction failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        # Fetch insider transactions if requested
        if any(f.startswith("insider.") for f in requested):
            try:
                fetched |= self._fetch_insider_data(
                    ticker, requested, data, source_metadata
                )
            except Exception as exc:
                msg = f"SEC EDGAR insider data fetch failed for {ticker}: {exc}"
                logger.warning(msg)
                warnings.append(msg)

        return data, source_metadata, fetched, warnings

    def fetch_insider_transactions(
        self, ticker: str, limit: int = 100
    ) -> list[Dict[str, Any]]:
        """
        Fetch recent insider transactions (Form 4 filings) for a ticker.

        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of transactions to return

        Returns:
            List of insider transaction records.
        """
        cik = self.get_cik(ticker)
        if not cik:
            return []

        try:
            # Get company submissions which includes recent filings
            submissions = self._make_request(f"/submissions/CIK{cik}.json")

            filings = submissions.get("filings", {}).get("recent", {})
            form_types = filings.get("form", [])
            filing_dates = filings.get("filingDate", [])
            accession_numbers = filings.get("accessionNumber", [])
            primary_documents = filings.get("primaryDocument", [])

            # Filter for Form 4 (insider transactions)
            transactions = []
            for i, form_type in enumerate(form_types):
                if form_type in ("4", "4/A") and len(transactions) < limit:
                    transactions.append({
                        "form_type": form_type,
                        "filing_date": filing_dates[i] if i < len(filing_dates) else None,
                        "accession_number": accession_numbers[i] if i < len(accession_numbers) else None,
                        "document": primary_documents[i] if i < len(primary_documents) else None,
                    })

            return transactions

        except Exception as exc:
            logger.error(f"Failed to fetch insider transactions for {ticker}: {exc}")
            return []

    # -------- internal helpers --------

    def _make_request(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make rate-limited request to SEC EDGAR API (data.sec.gov)."""
        return self._make_request_url(f"{self.BASE_URL}{path}", params)

    def _make_request_url(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make rate-limited request to a full URL."""
        # Rate limiting: max 10 requests/second
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

        response = self.session.get(url, params=params, headers=headers, timeout=30)
        self._last_request_time = time.time()

        response.raise_for_status()
        return response.json()

    def _extract_xbrl_data(
        self,
        us_gaap: Dict[str, Any],
        requested: Set[str],
        period: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        """Extract XBRL data from us-gaap facts."""
        fetched: Set[str] = set()
        form_filter = "10-K" if period == "annual" else "10-Q"

        # Field mappings: (requested_field, xbrl_tag, data_section)
        field_mappings = [
            # Balance sheet items not in other APIs
            ("financials.goodwill", "Goodwill", "financials"),
            ("financials.intangible_assets", "IntangibleAssetsNetExcludingGoodwill", "financials"),
            ("financials.other_intangible_assets", "OtherIntangibleAssetsNet", "financials"),

            # Income statement items not in other APIs
            ("financials.research_and_development", "ResearchAndDevelopmentExpense", "financials"),
            ("financials.selling_general_admin", "SellingGeneralAndAdministrativeExpense", "financials"),
            ("financials.cost_of_goods_sold", "CostOfGoodsAndServicesSold", "financials"),

            # Fallback fields (in case primary APIs fail)
            ("financials.revenue", "Revenues", "financials"),
            ("financials.revenue_alt", "RevenueFromContractWithCustomerExcludingAssessedTax", "financials"),
            ("financials.net_income", "NetIncomeLoss", "financials"),
            ("financials.total_assets", "Assets", "financials"),
            ("financials.total_liabilities", "Liabilities", "financials"),
            ("financials.stockholders_equity", "StockholdersEquity", "financials"),
            ("financials.shares_outstanding", "CommonStockSharesOutstanding", "financials"),
        ]

        for field_id, xbrl_tag, section in field_mappings:
            if field_id not in requested:
                continue

            concept = us_gaap.get(xbrl_tag)
            if not concept:
                # Try alternative tags
                alt_tags = self._get_alternative_tags(xbrl_tag)
                for alt_tag in alt_tags:
                    concept = us_gaap.get(alt_tag)
                    if concept:
                        break

            if not concept:
                continue

            # Get units (usually USD for monetary, shares for counts)
            units = concept.get("units", {})
            values = units.get("USD") or units.get("shares") or units.get("pure", [])

            if not values:
                continue

            # Filter by form type and get most recent value
            filtered = [
                v for v in values
                if v.get("form") == form_filter or (form_filter == "10-K" and v.get("form") == "10-K/A")
            ]

            if not filtered:
                # Fall back to any value
                filtered = values

            # Sort by end date descending and get most recent
            filtered.sort(key=lambda x: x.get("end", ""), reverse=True)

            if filtered:
                most_recent = filtered[0]
                value = most_recent.get("val")

                if value is not None:
                    key = field_id.split(".", 1)[1]
                    data[section][key] = value
                    metadata[field_id] = {
                        "provider": "sec_edgar",
                        "timestamp": most_recent.get("end", ""),
                        "form": most_recent.get("form", ""),
                        "xbrl_tag": xbrl_tag,
                        "endpoint": "/api/xbrl/companyfacts",
                    }
                    fetched.add(field_id)

        # Build historical data
        self._build_xbrl_history(us_gaap, form_filter, data)

        return fetched

    def _get_alternative_tags(self, xbrl_tag: str) -> list[str]:
        """Get alternative XBRL tags for common fields."""
        alternatives = {
            "Revenues": [
                "RevenueFromContractWithCustomerExcludingAssessedTax",
                "SalesRevenueNet",
                "TotalRevenuesAndOtherIncome",
            ],
            "ResearchAndDevelopmentExpense": [
                "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
            ],
            "IntangibleAssetsNetExcludingGoodwill": [
                "OtherIntangibleAssetsNet",
                "FiniteLivedIntangibleAssetsNet",
            ],
            "StockholdersEquity": [
                "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            ],
            "CommonStockSharesOutstanding": [
                "WeightedAverageNumberOfSharesOutstandingBasic",
                "WeightedAverageNumberOfDilutedSharesOutstanding",
            ],
        }
        return alternatives.get(xbrl_tag, [])

    def _build_xbrl_history(
        self,
        us_gaap: Dict[str, Any],
        form_filter: str,
        data: Dict[str, Any],
    ) -> None:
        """Build historical data from XBRL facts."""
        # Key metrics to track historically
        history_tags = {
            "goodwill": "Goodwill",
            "intangible_assets": "IntangibleAssetsNetExcludingGoodwill",
            "research_and_development": "ResearchAndDevelopmentExpense",
            "selling_general_admin": "SellingGeneralAndAdministrativeExpense",
        }

        sec_history: Dict[str, list] = {}

        for key, xbrl_tag in history_tags.items():
            concept = us_gaap.get(xbrl_tag)
            if not concept:
                continue

            units = concept.get("units", {})
            values = units.get("USD") or units.get("shares", [])

            # Filter and sort by end date
            filtered = [
                v for v in values
                if v.get("form") in (form_filter, f"{form_filter}/A")
            ]
            filtered.sort(key=lambda x: x.get("end", ""), reverse=True)

            # Store up to 10 years of data
            sec_history[key] = [
                {"period": v.get("end"), "value": v.get("val")}
                for v in filtered[:10]
            ]

        if sec_history:
            data["sec_edgar"]["history"] = sec_history

    def _fetch_insider_data(
        self,
        ticker: str,
        requested: Set[str],
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        """Fetch insider transaction data."""
        fetched: Set[str] = set()

        transactions = self.fetch_insider_transactions(ticker)

        if transactions:
            data["sec_edgar"]["insider_transactions"] = transactions
            data["sec_edgar"]["insider_transaction_count"] = len(transactions)

            if "insider.transactions" in requested:
                metadata["insider.transactions"] = {
                    "provider": "sec_edgar",
                    "endpoint": "/submissions",
                    "count": len(transactions),
                }
                fetched.add("insider.transactions")

        return fetched

    def get_xbrl_value(
        self,
        ticker: str,
        xbrl_tag: str,
        period: str = "annual",
        fiscal_year: Optional[int] = None,
    ) -> Optional[float]:
        """
        Get a specific XBRL value for a company.

        Args:
            ticker: Stock ticker symbol
            xbrl_tag: XBRL concept tag (e.g., "Goodwill")
            period: "annual" or "quarterly"
            fiscal_year: Optional specific fiscal year

        Returns:
            Value or None if not found.
        """
        company_facts = self.fetch_company_facts(ticker)
        if not company_facts:
            return None

        us_gaap = company_facts.get("facts", {}).get("us-gaap", {})
        concept = us_gaap.get(xbrl_tag)

        if not concept:
            return None

        units = concept.get("units", {})
        values = units.get("USD") or units.get("shares", [])

        form_filter = "10-K" if period == "annual" else "10-Q"
        filtered = [
            v for v in values
            if v.get("form") == form_filter
        ]

        if fiscal_year:
            filtered = [
                v for v in filtered
                if v.get("fy") == fiscal_year
            ]

        if not filtered:
            return None

        # Get most recent
        filtered.sort(key=lambda x: x.get("end", ""), reverse=True)
        return filtered[0].get("val")
