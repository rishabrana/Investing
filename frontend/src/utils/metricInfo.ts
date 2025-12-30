/**
 * Metric information for tooltips and external links
 */

export interface MetricInfo {
  description: string;
  learnMoreUrl?: string;
}

export const metricInfoMap: Record<string, MetricInfo> = {
  // Profitability Metrics
  'roic': {
    description: 'Return on Invested Capital measures how effectively management turns all long-term capital (debt and equity) into operating profit after tax. Higher is better.',
    learnMoreUrl: 'https://www.investopedia.com/terms/r/returnoninvestmentcapital.asp',
  },
  'roe': {
    description: 'Return on Equity reveals how efficiently the company turns shareholder capital into bottom-line profit. A consistently high ROE indicates strong profitability.',
    learnMoreUrl: 'https://www.investopedia.com/terms/r/returnonequity.asp',
  },
  'operating_margin': {
    description: 'Operating Margin shows operating profit as a percentage of revenue. It measures how much profit a company makes on each dollar of sales before interest and taxes.',
    learnMoreUrl: 'https://www.investopedia.com/terms/o/operatingmargin.asp',
  },
  'net_margin': {
    description: 'Net Margin shows net profit as a percentage of revenue. It represents how much profit remains after all expenses, including taxes and interest.',
    learnMoreUrl: 'https://www.investopedia.com/terms/n/net_margin.asp',
  },
  'eps_growth': {
    description: 'Earnings Per Share Growth tracks how quickly earnings per share compound over time. It\'s a key indicator of a company\'s growth engine.',
    learnMoreUrl: 'https://www.investopedia.com/terms/e/eps.asp',
  },
  'book_value_growth': {
    description: 'Book Value Per Share Growth measures the increase in net asset value per share over time. Growing book value indicates wealth creation for shareholders.',
    learnMoreUrl: 'https://www.investopedia.com/terms/b/bookvaluepercommon.asp',
  },
  'ten_year_average_roce': {
    description: 'Ten-Year Average Return on Capital Employed measures long-term capital efficiency. Consistent high ROCE indicates a durable competitive advantage.',
    learnMoreUrl: 'https://www.investopedia.com/terms/r/roce.asp',
  },

  // Valuation Metrics
  'pe_ratio': {
    description: 'Price-to-Earnings Ratio compares stock price to earnings per share. Lower P/E may indicate undervaluation, but should be compared to industry peers.',
    learnMoreUrl: 'https://www.investopedia.com/terms/p/price-earningsratio.asp',
  },
  'peg_ratio': {
    description: 'Price/Earnings to Growth Ratio adjusts P/E for earnings growth. A PEG below 1.0 may indicate the stock is undervalued relative to its growth rate.',
    learnMoreUrl: 'https://www.investopedia.com/terms/p/pegratio.asp',
  },
  'pb_ratio': {
    description: 'Price-to-Book Ratio compares stock price to book value per share. Lower P/B may indicate undervaluation, especially for asset-heavy businesses.',
    learnMoreUrl: 'https://www.investopedia.com/terms/p/price-to-bookratio.asp',
  },
  'ps_ratio': {
    description: 'Price-to-Sales Ratio compares stock price to revenue per share. Useful for valuing companies with low or negative earnings.',
    learnMoreUrl: 'https://www.investopedia.com/terms/p/price-to-salesratio.asp',
  },
  'margin_of_safety': {
    description: 'Margin of Safety compares intrinsic value to market price, showing the discount or premium. A positive margin suggests the stock trades below its true worth.',
    learnMoreUrl: 'https://www.investopedia.com/terms/m/marginofsafety.asp',
  },
  'ev_to_ebitda': {
    description: 'Enterprise Value to EBITDA compares total company value to earnings before interest, taxes, depreciation, and amortization. Useful for comparing companies with different capital structures.',
    learnMoreUrl: 'https://www.investopedia.com/terms/e/ev-ebitda.asp',
  },
  'dividend_yield': {
    description: 'Dividend Yield shows annual dividends as a percentage of stock price. Higher yields can provide income, but very high yields may signal financial distress.',
    learnMoreUrl: 'https://www.investopedia.com/terms/d/dividendyield.asp',
  },

  // Cash Generation Metrics
  'free_cash_flow': {
    description: 'Free Cash Flow shows how much cash the business generates after maintaining its assets. This cash can pay dividends, reduce debt, or fund growth.',
    learnMoreUrl: 'https://www.investopedia.com/terms/f/freecashflow.asp',
  },
  'fcf_margin': {
    description: 'Free Cash Flow Margin expresses FCF as a percentage of revenue. Higher margins indicate the company efficiently converts sales into cash.',
    learnMoreUrl: 'https://www.investopedia.com/terms/f/freecashflow.asp',
  },
  'fcf_per_share': {
    description: 'Free Cash Flow Per Share divides total FCF by shares outstanding. Growing FCF per share indicates increasing value creation for each shareholder.',
    learnMoreUrl: 'https://www.investopedia.com/terms/f/freecashflow.asp',
  },
  'operating_cash_flow': {
    description: 'Operating Cash Flow measures cash generated from normal business operations. Strong OCF indicates a healthy, sustainable business model.',
    learnMoreUrl: 'https://www.investopedia.com/terms/o/operatingcashflow.asp',
  },
  'capex_to_revenue': {
    description: 'Capital Expenditure to Revenue shows how much of each revenue dollar must be reinvested in assets. Lower ratios suggest less capital-intensive businesses.',
    learnMoreUrl: 'https://www.investopedia.com/terms/c/capitalexpenditure.asp',
  },

  // Financial Strength Metrics
  'debt_to_equity': {
    description: 'Debt-to-Equity Ratio compares total debt to shareholder equity. Lower ratios indicate less financial leverage and lower bankruptcy risk.',
    learnMoreUrl: 'https://www.investopedia.com/terms/d/debtequityratio.asp',
  },
  'interest_coverage': {
    description: 'Interest Coverage shows how many times operating profit can cover interest expense. Higher coverage indicates greater ability to service debt.',
    learnMoreUrl: 'https://www.investopedia.com/terms/i/interestcoverageratio.asp',
  },
  'current_ratio': {
    description: 'Current Ratio compares current assets to current liabilities. A ratio above 1.0 indicates the company can cover short-term obligations.',
    learnMoreUrl: 'https://www.investopedia.com/terms/c/currentratio.asp',
  },
  'quick_ratio': {
    description: 'Quick Ratio (Acid Test) measures ability to pay short-term obligations using only the most liquid assets. More conservative than current ratio.',
    learnMoreUrl: 'https://www.investopedia.com/terms/q/quickratio.asp',
  },
  'cash_to_debt': {
    description: 'Cash to Debt Ratio shows how much cash is available relative to total debt. Higher ratios indicate better ability to pay down debt.',
    learnMoreUrl: 'https://www.investopedia.com/terms/c/cash-debt-ratio.asp',
  },

  // Capital Allocation Metrics
  'dividend_payout_ratio': {
    description: 'Dividend Payout Ratio shows what percentage of earnings is paid out as dividends. Lower ratios suggest more earnings retained for growth.',
    learnMoreUrl: 'https://www.investopedia.com/terms/d/dividendpayoutratio.asp',
  },
  'buyback_yield': {
    description: 'Buyback Yield measures share repurchases as a percentage of market cap. Companies buying back shares reduce share count and increase per-share value.',
    learnMoreUrl: 'https://www.investopedia.com/terms/b/buyback.asp',
  },
  'total_payout_ratio': {
    description: 'Total Payout Ratio combines dividends and buybacks to show total capital returned to shareholders. Indicates management\'s capital allocation priorities.',
    learnMoreUrl: 'https://www.investopedia.com/terms/t/total-payout-ratio.asp',
  },
  'retention_rate': {
    description: 'Retention Rate shows what percentage of earnings is kept in the business for reinvestment. Higher retention can fuel growth if ROIC is strong.',
    learnMoreUrl: 'https://www.investopedia.com/terms/r/retentionratio.asp',
  },

  // Moat Metrics
  'market_share': {
    description: 'Market Share shows the company\'s portion of total industry sales. High and growing market share can indicate competitive advantages.',
    learnMoreUrl: 'https://www.investopedia.com/terms/m/marketshare.asp',
  },
  'pricing_power': {
    description: 'Pricing Power measures ability to raise prices without losing customers. Strong pricing power is a key indicator of a competitive moat.',
    learnMoreUrl: 'https://www.investopedia.com/terms/p/pricingpower.asp',
  },
  'brand_value': {
    description: 'Brand Value estimates the monetary value of the company\'s brand. Strong brands command premium prices and customer loyalty.',
    learnMoreUrl: 'https://www.investopedia.com/terms/b/brandequity.asp',
  },
  'customer_concentration': {
    description: 'Customer Concentration measures reliance on top customers. Lower concentration reduces business risk from losing a single customer.',
    learnMoreUrl: 'https://www.investopedia.com/terms/c/concentration-risk.asp',
  },
  'switching_costs': {
    description: 'Switching Costs measure how difficult it is for customers to switch to competitors. High switching costs create customer stickiness.',
    learnMoreUrl: 'https://www.investopedia.com/terms/s/switchingcosts.asp',
  },
};

/**
 * Get metric information for tooltips
 */
export function getMetricInfo(metricKey: string): MetricInfo | undefined {
  return metricInfoMap[metricKey.toLowerCase()];
}
