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
  fetched_at?: string | null;
}

export interface ValuationMetrics {
  price_to_earnings?: number;
  forward_pe?: number;
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
  earnings_stability?: {
    positive_years: number;
    total_years: number;
    stability_percentage: number;
    meets_criteria: boolean;
    classification: string;
  };
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
  current_ratio?: number;
}

export interface CapitalAllocationMetrics {
  dividend_yield_and_payout_ratio?: {
    dividend_yield: number;
    payout_ratio: number;
  };
  dividend_history?: {
    pays_dividends: boolean;
    years_of_dividends: number;
    consecutive_years: number;
    growth_years: number;
    avg_growth_rate: number | null;
    is_aristocrat: boolean;
    meets_5year_criteria: boolean;
    classification: string;
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
  piotroski_fscore?: {
    score: number;
    max_score: number;
    classification: string;
    components: Record<string, number>;
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

export interface ValidateTickersBatchRequest {
  symbols: string[];
}

export interface ValidateTickerResult {
  is_valid: boolean;
  symbol: string;
  company_name: string | null;
  error: string | null;
}

export interface ValidateTickersBatchResponse {
  results: ValidateTickerResult[];
  valid_count: number;
  invalid_count: number;
}

export interface AddTickersBatchRequest {
  symbols: string[];
  skip_validation?: boolean;
}

export interface AddTickerBatchResult {
  symbol: string;
  success: boolean;
  message: string;
  company_name?: string | null;
  error?: string | null;
}

export interface AddTickersBatchResponse {
  results: AddTickerBatchResult[];
  added_count: number;
  failed_count: number;
  skipped_count: number;
}

export interface RefreshStockRequest {
  force?: boolean;
}

// UI State Types

export interface SectionVisibility {
  valuation: boolean;
  profitability: boolean;
  cash_generation: boolean;
  financial_strength: boolean;
  capital_allocation: boolean;
  moat: boolean;
}

export type ViewMode = 'metrics' | 'logs' | 'screener';

export interface AppState {
  selectedTicker: string | null;
  setSelectedTicker: (ticker: string | null) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  sectionVisibility: SectionVisibility;
  setSectionVisibility: (visibility: SectionVisibility) => void;
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
}

// Value Screener Types

export interface ScreenerScore {
  metric_name: string;
  value: number | null;
  score: number; // 0-1 where 1 is best
  passes: boolean;
  target: string;
}

export interface ScreenedStock {
  ticker: string;
  name: string | null;
  overall_score: number; // 0-1
  total_points: number; // Out of max possible
  max_points: number;
  scores: ScreenerScore[];
  price: number | null;
  market_cap: number | null;
}

export interface ScreenerResponse {
  stocks: ScreenedStock[];
  screened_at: string;
  criteria_count: number;
}

export type MetricCategory =
  | 'valuation'
  | 'profitability'
  | 'cash_generation'
  | 'financial_strength'
  | 'capital_allocation'
  | 'moat';

// Log Types

export type LogLevel = 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
export type OperationType = 'API_CALL' | 'METRICS_CALCULATION' | 'DATA_FETCH' | 'DATA_VALIDATION';

export interface LogEntry {
  timestamp: string;
  operation_type: OperationType;
  level: LogLevel;
  message: string;
  ticker?: string;
  provider?: string;
  duration_ms?: number;
  error?: string;
  details?: Record<string, any>;
}

export interface LogsResponse {
  count: number;
  hours: number;
  operation_type?: string;
  errors: LogEntry[];
}
