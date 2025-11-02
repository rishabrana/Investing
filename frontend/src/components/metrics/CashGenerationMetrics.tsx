import { MetricSection } from './MetricSection';
import { MetricWithChart } from './MetricWithChart';
import { CashGenerationMetrics as CashGenerationMetricsType } from '@/types';
import { formatCurrency, formatPercent } from '@/utils/formatters';
import { useStockHistory } from '@/hooks/useStock';

interface CashGenerationMetricsProps {
  ticker: string;
  metrics: CashGenerationMetricsType;
}

export function CashGenerationMetrics({ ticker, metrics }: CashGenerationMetricsProps) {
  const { data: fcfHistory } = useStockHistory(ticker, 'free_cash_flow', 10);
  const getCapexColor = (value: number | undefined) => {
    if (!value) return 'default';
    if (value <= 0.10) return 'positive';  // 10% or less is good
    if (value <= 0.20) return 'warning';   // 10-20% is okay
    return 'negative';                     // >20% is concerning
  };

  return (
    <MetricSection
      title="Cash Generation"
      description="The company's ability to generate cash from its operations"
    >
      <MetricWithChart
        label="Free Cash Flow"
        currentValue={metrics.free_cash_flow}
        historicalData={fcfHistory?.data_points}
        formatter={(v) => formatCurrency(v)}
        description="Cash after capital expenditures"
        color={metrics.free_cash_flow && metrics.free_cash_flow > 0 ? 'positive' : 'negative'}
        chartColor="#10b981"
      />
      <MetricWithChart
        label="Owner Earnings"
        currentValue={metrics.owner_earnings}
        formatter={(v) => formatCurrency(v)}
        description="Buffett's measure of true earnings"
        color={metrics.owner_earnings && metrics.owner_earnings > 0 ? 'positive' : 'negative'}
        chartColor="#3b82f6"
      />
      <MetricWithChart
        label="CapEx Ratio"
        currentValue={metrics.capital_expenditure_ratio}
        formatter={(v) => formatPercent(v, 1)}
        description="Capital expenditures as % of revenue"
        color={getCapexColor(metrics.capital_expenditure_ratio)}
        chartColor="#8b5cf6"
      />
    </MetricSection>
  );
}
