// API Response Types

export interface TickerEntry {
  symbol: string;
  name: string | null;
  notes: string | null;
  metrics_profile: string | null;
}

export interface Watchlist {
  name: string;
  default_metrics_profile: string;
  tickers: TickerEntry[];
  total_count: number;
}

export interface PriceData {
  close: number;
  open: number | null;
  high: number | null;
  low: number | null;
  change: number | null;
  change_percent: number | null;
  as_of: string;
}

export interface MarketData {
  market_cap: number | null;
  shares_outstanding: number | null;
}

export interface StockOverview {
  ticker: string;
  name: string | null;
  price: PriceData;
  market_data: MarketData;
}

export interface ValuationMetrics {
  price_to_earnings?: number;
  price_to_book?: number;
  ev_to_ebitda?: number;
  peg_ratio?: number;
}

export interface ProfitabilityMetrics {
  return_on_invested_capital?: number;
  return_on_equity?: number;
  operating_and_net_margin?: {
    operating_margin: number;
    net_margin: number;
  };
  eps_growth?: number;
  book_value_per_share_growth?: number;
  ten_year_average_roce?: number;
}

export interface CashGenerationMetrics {
  free_cash_flow?: number;
  owner_earnings?: number;
  capital_expenditure_ratio?: number;
}

export interface FinancialStrengthMetrics {
  debt_to_equity_and_interest_coverage?: {
    debt_to_equity: number;
    interest_coverage: number | null;
  };
}

export interface CapitalAllocationMetrics {
  dividend_yield_and_payout_ratio?: {
    dividend_yield: number;
    payout_ratio: number;
  };
  wacc_vs_roic_spread?: number;
}

export interface MoatMetrics {
  economic_moat_score?: {
    score: number;
    label: string;
    margin_stability: number;
    roic_trend: number;
    revenue_cagr: number;
  };
  consistency_score?: {
    score: number;
    label: string;
  };
}

export interface StockMetrics {
  ticker: string;
  as_of: string;
  calculated_at: string;
  profile_used: string;
  valuation: ValuationMetrics;
  profitability: ProfitabilityMetrics;
  cash_generation: CashGenerationMetrics;
  financial_strength: FinancialStrengthMetrics;
  capital_allocation: CapitalAllocationMetrics;
  moat: MoatMetrics;
  growth: Record<string, any>;
}

export interface HistoryDataPoint {
  period: string;
  value: number | null;
}

export interface StockHistory {
  ticker: string;
  metric: string;
  data_points: HistoryDataPoint[];
}

// API Request Types

export interface AddTickerRequest {
  symbol: string;
  name?: string;
  notes?: string;
  skip_validation?: boolean;
}

export interface ValidateTickerRequest {
  symbol: string;
}

export interface RefreshStockRequest {
  force?: boolean;
}

// UI State Types

export interface AppState {
  selectedTicker: string | null;
  setSelectedTicker: (ticker: string | null) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export type MetricCategory =
  | 'valuation'
  | 'profitability'
  | 'cash_generation'
  | 'financial_strength'
  | 'capital_allocation'
  | 'moat';
