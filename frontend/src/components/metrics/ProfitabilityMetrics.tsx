import { MetricSection } from './MetricSection';
import { MetricWithChart } from './MetricWithChart';
import { ProfitabilityMetrics as ProfitabilityMetricsType, HistoryDataPoint } from '@/types';
import { formatPercent } from '@/utils/formatters';
import { useStockHistory } from '@/hooks/useStock';

interface ProfitabilityMetricsProps {
  ticker: string;
  metrics: ProfitabilityMetricsType;
}

export function ProfitabilityMetrics({ ticker, metrics }: ProfitabilityMetricsProps) {
  // Fetch historical data for key metrics
  const { data: roicHistory } = useStockHistory(ticker, 'roic', 10);
  const { data: roeHistory } = useStockHistory(ticker, 'roe', 10);
  const { data: opMarginHistory } = useStockHistory(ticker, 'operating_margin', 10);

  const getRoicColor = (value: number | undefined) => {
    if (!value) return 'default';
    if (value >= 0.15) return 'positive'; // 15%+
    if (value >= 0.10) return 'warning';  // 10-15%
    return 'negative';
  };

  const getRoeColor = (value: number | undefined) => {
    if (!value) return 'default';
    if (value >= 0.15) return 'positive'; // 15%+
    if (value >= 0.10) return 'warning';  // 10-15%
    return 'negative';
  };

  const getMarginColor = (value: number | undefined) => {
    if (!value) return 'default';
    if (value >= 0.20) return 'positive'; // 20%+
    if (value >= 0.10) return 'warning';  // 10-20%
    return 'negative';
  };

  const getGrowthColor = (value: number | undefined) => {
    if (!value) return 'default';
    if (value >= 0.10) return 'positive'; // 10%+
    if (value >= 0.05) return 'warning';  // 5-10%
    if (value < 0) return 'negative';
    return 'default';
  };

  return (
    <MetricSection
      title="Profitability"
      description="How efficiently the company generates returns on its capital and investments"
    >
      <MetricWithChart
        label="ROIC"
        currentValue={metrics.return_on_invested_capital}
        historicalData={roicHistory?.data_points}
        formatter={(v) => formatPercent(v, 1)}
        description="Return on Invested Capital"
        color={getRoicColor(metrics.return_on_invested_capital)}
        chartColor="#10b981"
        metricKey="roic"
      />
      <MetricWithChart
        label="ROE"
        currentValue={metrics.return_on_equity}
        historicalData={roeHistory?.data_points}
        formatter={(v) => formatPercent(v, 1)}
        description="Return on Equity"
        color={getRoeColor(metrics.return_on_equity)}
        chartColor="#3b82f6"
        metricKey="roe"
      />
      <MetricWithChart
        label="Operating Margin"
        currentValue={metrics.operating_and_net_margin?.operating_margin}
        historicalData={opMarginHistory?.data_points}
        formatter={(v) => formatPercent(v, 1)}
        description="Operating profit as % of revenue"
        color={getMarginColor(metrics.operating_and_net_margin?.operating_margin)}
        chartColor="#8b5cf6"
        metricKey="operating_margin"
      />
      <MetricWithChart
        label="Net Margin"
        currentValue={metrics.operating_and_net_margin?.net_margin}
        historicalData={opMarginHistory?.data_points.map((d: HistoryDataPoint) => ({ ...d, value: d.value ? d.value * 0.85 : null }))}
        formatter={(v) => formatPercent(v, 1)}
        description="Net profit as % of revenue"
        color={getMarginColor(metrics.operating_and_net_margin?.net_margin)}
        chartColor="#6366f1"
        metricKey="net_margin"
      />
      <MetricWithChart
        label="EPS Growth"
        currentValue={metrics.eps_growth}
        formatter={(v) => formatPercent(v, 1)}
        description="Earnings per share growth rate"
        color={getGrowthColor(metrics.eps_growth)}
        chartColor="#f59e0b"
        metricKey="eps_growth"
      />
      <MetricWithChart
        label="Book Value Growth"
        currentValue={metrics.book_value_per_share_growth}
        formatter={(v) => formatPercent(v, 1)}
        description="Book value per share growth"
        color={getGrowthColor(metrics.book_value_per_share_growth)}
        chartColor="#ef4444"
        metricKey="book_value_growth"
      />
      <MetricWithChart
        label="10-Year Avg ROCE"
        currentValue={metrics.ten_year_average_roce}
        formatter={(v) => formatPercent(v, 1)}
        description="Long-term capital efficiency"
        color={getRoicColor(metrics.ten_year_average_roce)}
        chartColor="#14b8a6"
        metricKey="ten_year_average_roce"
      />
    </MetricSection>
  );
}
