/**
 * Format a number as currency (USD)
 */
export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';

  // Handle billions/millions
  if (Math.abs(value) >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(2)}B`;
  } else if (Math.abs(value) >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(2)}M`;
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format a number as a percentage
 */
export function formatPercent(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return 'N/A';

  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a ratio (e.g., P/E ratio)
 */
export function formatRatio(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return 'N/A';

  return value.toFixed(decimals);
}

/**
 * Format a large number with commas
 */
export function formatNumber(value: number | null | undefined, decimals: number = 0): string {
  if (value === null || value === undefined) return 'N/A';

  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format a change value with +/- sign
 */
export function formatChange(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return 'N/A';

  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}`;
}

/**
 * Get color class for positive/negative values
 */
export function getChangeColorClass(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'text-neutral';
  return value >= 0 ? 'text-secondary' : 'text-danger';
}

/**
 * Format date string
 */
export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(date);
  } catch {
    return dateString;
  }
}

/**
 * Get metric display name from key
 */
export function getMetricDisplayName(key: string): string {
  const nameMap: Record<string, string> = {
    price_to_earnings: 'P/E Ratio',
    price_to_book: 'P/B Ratio',
    ev_to_ebitda: 'EV/EBITDA',
    peg_ratio: 'PEG Ratio',
    return_on_invested_capital: 'ROIC',
    return_on_equity: 'ROE',
    operating_margin: 'Operating Margin',
    net_margin: 'Net Margin',
    eps_growth: 'EPS Growth',
    book_value_per_share_growth: 'Book Value Growth',
    ten_year_average_roce: '10-Year Avg ROCE',
    free_cash_flow: 'Free Cash Flow',
    owner_earnings: 'Owner Earnings',
    capital_expenditure_ratio: 'CapEx Ratio',
    debt_to_equity: 'Debt/Equity',
    interest_coverage: 'Interest Coverage',
    dividend_yield: 'Dividend Yield',
    payout_ratio: 'Payout Ratio',
    wacc_vs_roic_spread: 'WACC vs ROIC Spread',
  };

  return nameMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}
