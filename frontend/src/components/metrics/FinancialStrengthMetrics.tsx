import { MetricSection } from './MetricSection';
import { MetricCard } from './MetricCard';
import { FinancialStrengthMetrics as FinancialStrengthMetricsType } from '@/types';
import { formatRatio } from '@/utils/formatters';

interface FinancialStrengthMetricsProps {
  metrics: FinancialStrengthMetricsType;
}

export function FinancialStrengthMetrics({ metrics }: FinancialStrengthMetricsProps) {
  const getDebtToEquityColor = (value: number | undefined) => {
    if (!value) return 'default';
    if (value <= 0.5) return 'positive';   // Low debt
    if (value <= 1.5) return 'warning';    // Moderate debt
    return 'negative';                     // High debt
  };

  const getInterestCoverageColor = (value: number | null | undefined) => {
    if (!value) return 'default';
    if (value >= 10) return 'positive';    // Very comfortable
    if (value >= 5) return 'warning';      // Adequate
    return 'negative';                     // Concerning
  };

  return (
    <MetricSection
      title="Financial Strength"
      description="The company's balance sheet health and ability to meet obligations"
    >
      <MetricCard
        label="Debt/Equity"
        value={metrics.debt_to_equity_and_interest_coverage?.debt_to_equity}
        formatter={(v) => formatRatio(v, 2)}
        description="Total debt relative to equity"
        color={getDebtToEquityColor(metrics.debt_to_equity_and_interest_coverage?.debt_to_equity)}
      />
      <MetricCard
        label="Interest Coverage"
        value={metrics.debt_to_equity_and_interest_coverage?.interest_coverage}
        formatter={(v) => formatRatio(v, 1)}
        description="Ability to cover interest payments"
        color={getInterestCoverageColor(metrics.debt_to_equity_and_interest_coverage?.interest_coverage)}
      />
    </MetricSection>
  );
}
