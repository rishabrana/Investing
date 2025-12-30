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
        infoDescription="A company's sustainable competitive advantage that protects it from competitors. Wide moats indicate strong, durable advantages like brand power, network effects, or cost advantages."
        infoUrl="https://www.investopedia.com/terms/e/economicmoat.asp"
      />
      <MetricCard
        label="Margin Stability"
        value={metrics.economic_moat_score?.margin_stability}
        formatter={(v) => formatPercent(v, 1)}
        description="Consistency of profit margins"
        color={metrics.economic_moat_score?.margin_stability && metrics.economic_moat_score.margin_stability >= 0.7 ? 'positive' : 'warning'}
        infoDescription="Measures how consistent profit margins are over time. High stability indicates pricing power and a durable competitive advantage."
        infoUrl="https://www.investopedia.com/terms/p/profitmargin.asp"
      />
      <MetricCard
        label="ROIC Trend"
        value={metrics.economic_moat_score?.roic_trend}
        formatter={(v) => formatPercent(v, 1)}
        description="Return on capital trajectory"
        color={metrics.economic_moat_score?.roic_trend && metrics.economic_moat_score.roic_trend > 0 ? 'positive' : 'negative'}
        infoDescription="The trend in Return on Invested Capital over time. Improving ROIC suggests strengthening competitive advantages and better capital efficiency."
        infoUrl="https://www.investopedia.com/terms/r/returnoninvestmentcapital.asp"
      />
      <MetricCard
        label="Revenue CAGR"
        value={metrics.economic_moat_score?.revenue_cagr}
        formatter={(v) => formatPercent(v, 1)}
        description="Compound annual growth rate"
        color={metrics.economic_moat_score?.revenue_cagr && metrics.economic_moat_score.revenue_cagr >= 0.05 ? 'positive' : 'warning'}
        infoDescription="Compound Annual Growth Rate of revenue, showing how quickly the company's top line is expanding over time."
        infoUrl="https://www.investopedia.com/terms/c/cagr.asp"
      />
      <MetricCard
        label="Consistency Score"
        value={metrics.consistency_score?.label?.toUpperCase() || 'N/A'}
        description={`Score: ${metrics.consistency_score?.score ? (metrics.consistency_score.score * 100).toFixed(1) + '%' : 'N/A'}`}
        color={getConsistencyColor(metrics.consistency_score?.label)}
        infoDescription="Measures how consistent the company's financial performance is over time. Consistent companies are more predictable and less risky."
        infoUrl="https://www.investopedia.com/terms/e/earnings-quality.asp"
      />
    </MetricSection>
  );
}
