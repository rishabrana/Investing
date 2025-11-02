import { MetricSection } from './MetricSection';
import { MetricCard } from './MetricCard';
import { MoatMetrics as MoatMetricsType } from '@/types';
import { formatPercent } from '@/utils/formatters';

interface MoatMetricsProps {
  metrics: MoatMetricsType;
}

export function MoatMetrics({ metrics }: MoatMetricsProps) {
  const getMoatScoreColor = (label: string | undefined) => {
    switch (label?.toLowerCase()) {
      case 'wide':
        return 'positive';
      case 'narrow':
        return 'warning';
      case 'none':
      default:
        return 'negative';
    }
  };

  const getConsistencyColor = (label: string | undefined) => {
    switch (label?.toLowerCase()) {
      case 'consistent':
        return 'positive';
      case 'moderate':
        return 'warning';
      case 'volatile':
      default:
        return 'negative';
    }
  };

  return (
    <MetricSection
      title="Economic Moat & Consistency"
      description="The company's competitive advantages and performance consistency"
    >
      <MetricCard
        label="Economic Moat"
        value={metrics.economic_moat_score?.label?.toUpperCase() || 'N/A'}
        description={`Score: ${metrics.economic_moat_score?.score ? (metrics.economic_moat_score.score * 100).toFixed(1) + '%' : 'N/A'}`}
        color={getMoatScoreColor(metrics.economic_moat_score?.label)}
      />
      <MetricCard
        label="Margin Stability"
        value={metrics.economic_moat_score?.margin_stability}
        formatter={(v) => formatPercent(v, 1)}
        description="Consistency of profit margins"
        color={metrics.economic_moat_score?.margin_stability && metrics.economic_moat_score.margin_stability >= 0.7 ? 'positive' : 'warning'}
      />
      <MetricCard
        label="ROIC Trend"
        value={metrics.economic_moat_score?.roic_trend}
        formatter={(v) => formatPercent(v, 1)}
        description="Return on capital trajectory"
        color={metrics.economic_moat_score?.roic_trend && metrics.economic_moat_score.roic_trend > 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        label="Revenue CAGR"
        value={metrics.economic_moat_score?.revenue_cagr}
        formatter={(v) => formatPercent(v, 1)}
        description="Compound annual growth rate"
        color={metrics.economic_moat_score?.revenue_cagr && metrics.economic_moat_score.revenue_cagr >= 0.05 ? 'positive' : 'warning'}
      />
      <MetricCard
        label="Consistency Score"
        value={metrics.consistency_score?.label?.toUpperCase() || 'N/A'}
        description={`Score: ${metrics.consistency_score?.score ? (metrics.consistency_score.score * 100).toFixed(1) + '%' : 'N/A'}`}
        color={getConsistencyColor(metrics.consistency_score?.label)}
      />
    </MetricSection>
  );
}
