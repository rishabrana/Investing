import { MetricSection } from './MetricSection';
import { MetricCard } from './MetricCard';
import { CapitalAllocationMetrics as CapitalAllocationMetricsType } from '@/types';
import { formatPercent } from '@/utils/formatters';

interface CapitalAllocationMetricsProps {
  metrics: CapitalAllocationMetricsType;
}

export function CapitalAllocationMetrics({ metrics }: CapitalAllocationMetricsProps) {
  const getSpreadColor = (value: number | undefined) => {
    if (!value) return 'default';
    if (value >= 0.05) return 'positive';  // 5%+ spread is excellent
    if (value >= 0) return 'warning';      // Positive spread is okay
    return 'negative';                     // Negative spread is bad
  };

  const getPayoutRatioColor = (value: number | undefined) => {
    if (!value) return 'default';
    if (value <= 0.5) return 'positive';   // 50% or less - sustainable
    if (value <= 0.75) return 'warning';   // 50-75% - moderate
    return 'negative';                     // >75% - high payout
  };

  return (
    <MetricSection
      title="Capital Allocation"
      description="How effectively management deploys capital and returns value to shareholders"
    >
      <MetricCard
        label="Dividend Yield"
        value={metrics.dividend_yield_and_payout_ratio?.dividend_yield}
        formatter={(v) => formatPercent(v, 2)}
        description="Annual dividend as % of stock price"
        color="default"
        metricKey="dividend_yield"
      />
      <MetricCard
        label="Payout Ratio"
        value={metrics.dividend_yield_and_payout_ratio?.payout_ratio}
        formatter={(v) => formatPercent(v, 1)}
        description="Dividends as % of earnings"
        color={getPayoutRatioColor(metrics.dividend_yield_and_payout_ratio?.payout_ratio)}
        metricKey="dividend_payout_ratio"
      />
      <MetricCard
        label="WACC vs ROIC Spread"
        value={metrics.wacc_vs_roic_spread}
        formatter={(v) => formatPercent(v, 1)}
        description="Value creation spread"
        color={getSpreadColor(metrics.wacc_vs_roic_spread)}
        infoDescription="The difference between Return on Invested Capital (ROIC) and Weighted Average Cost of Capital (WACC). A positive spread indicates the company creates value by earning returns above its cost of capital."
        infoUrl="https://www.investopedia.com/terms/r/returnoninvestmentcapital.asp"
      />
    </MetricSection>
  );
}
