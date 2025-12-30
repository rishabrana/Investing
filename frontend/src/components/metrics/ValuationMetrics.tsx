import { MetricSection } from './MetricSection';
import { MetricCard } from './MetricCard';
import { ValuationMetrics as ValuationMetricsType } from '@/types';
import { formatRatio } from '@/utils/formatters';

interface ValuationMetricsProps {
  metrics: ValuationMetricsType;
}

export function ValuationMetrics({ metrics }: ValuationMetricsProps) {
  const getValueColor = (value: number | undefined, thresholds: { low: number; high: number }) => {
    if (!value) return 'default';
    if (value < thresholds.low) return 'positive';
    if (value > thresholds.high) return 'negative';
    return 'warning';
  };

  return (
    <MetricSection
      title="Valuation"
      description="Key valuation ratios to assess whether the stock is trading at a reasonable price"
    >
      <MetricCard
        label="P/E Ratio (TTM)"
        value={metrics.price_to_earnings}
        formatter={(v) => formatRatio(v, 2)}
        description="Trailing Twelve Months P/E - Current valuation"
        color={getValueColor(metrics.price_to_earnings, { low: 15, high: 25 })}
        metricKey="pe_ratio"
      />
      <MetricCard
        label="Forward P/E"
        value={metrics.forward_pe}
        formatter={(v) => formatRatio(v, 2)}
        description="Forward P/E - Based on estimated earnings"
        color={getValueColor(metrics.forward_pe, { low: 12, high: 20 })}
        metricKey="pe_ratio"
      />
      <MetricCard
        label="P/B Ratio"
        value={metrics.price_to_book}
        formatter={(v) => formatRatio(v, 2)}
        description="Price to Book Value"
        color={getValueColor(metrics.price_to_book, { low: 1.5, high: 3 })}
        metricKey="pb_ratio"
      />
      <MetricCard
        label="EV/EBITDA"
        value={metrics.ev_to_ebitda}
        formatter={(v) => formatRatio(v, 2)}
        description="Enterprise Value to EBITDA"
        color={getValueColor(metrics.ev_to_ebitda, { low: 10, high: 15 })}
        metricKey="ev_to_ebitda"
      />
      <MetricCard
        label="PEG Ratio"
        value={metrics.peg_ratio}
        formatter={(v) => formatRatio(v, 2)}
        description="P/E to Growth - Below 1 is attractive"
        color={getValueColor(metrics.peg_ratio, { low: 1, high: 2 })}
        metricKey="peg_ratio"
      />
    </MetricSection>
  );
}
