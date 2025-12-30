import { ReactNode } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { InfoIcon } from '@/components/common/InfoIcon';
import { getMetricInfo } from '@/utils/metricInfo';

interface DataPoint {
  period: string;
  value: number | null;
}

interface MetricWithChartProps {
  label: string;
  currentValue: string | number | null | undefined;
  historicalData?: DataPoint[];
  formatter?: (value: any) => string;
  description?: string;
  color?: 'default' | 'positive' | 'negative' | 'warning';
  icon?: ReactNode;
  chartColor?: string;
  metricKey?: string; // Used to lookup info from metricInfoMap
  infoDescription?: string; // Override default description
  infoUrl?: string; // Override default learn more URL
}

export function MetricWithChart({
  label,
  currentValue,
  historicalData,
  formatter,
  description,
  color = 'default',
  icon,
  chartColor = '#3b82f6',
  metricKey,
  infoDescription,
  infoUrl,
}: MetricWithChartProps) {
  const formattedValue = formatter && currentValue !== null && currentValue !== undefined
    ? formatter(currentValue)
    : currentValue?.toString() ?? 'N/A';

  // Get metric info from the map or use overrides
  const metricInfo = metricKey ? getMetricInfo(metricKey) : undefined;
  const tooltipDescription = infoDescription || metricInfo?.description;
  const tooltipUrl = infoUrl || metricInfo?.learnMoreUrl;

  const badgeColorClasses = {
    default: 'bg-gray-100 text-gray-800',
    positive: 'bg-green-100 text-green-800',
    negative: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
  };

  // Filter out null values and prepare data for chart
  const chartData = historicalData?.filter(d => d.value !== null && d.value !== undefined) || [];
  const hasData = chartData.length > 0;

  // Format period for display (e.g., "2023-09-30" -> "2023")
  const formatPeriod = (period: string) => {
    return period.split('-')[0];
  };

  // Format Y-axis values based on the formatter
  const formatYAxis = (value: number) => {
    if (formatter) {
      return formatter(value);
    }
    // Default formatting for numbers
    if (Math.abs(value) >= 1e9) {
      return `${(value / 1e9).toFixed(1)}B`;
    }
    if (Math.abs(value) >= 1e6) {
      return `${(value / 1e6).toFixed(1)}M`;
    }
    if (Math.abs(value) >= 1e3) {
      return `${(value / 1e3).toFixed(1)}K`;
    }
    return value.toFixed(2);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            {icon && <span className="text-gray-400">{icon}</span>}
            <p className="text-sm font-medium text-gray-600">{label}</p>
            {tooltipDescription && (
              <InfoIcon
                description={tooltipDescription}
                learnMoreUrl={tooltipUrl}
                size="sm"
              />
            )}
          </div>
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
      </div>

      {/* Chart */}
      {hasData && (
        <div className="mb-3" style={{ height: '100px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <XAxis
                dataKey="period"
                tickFormatter={formatPeriod}
                tick={{ fontSize: 10 }}
                stroke="#9ca3af"
              />
              <YAxis
                tick={{ fontSize: 10 }}
                stroke="#9ca3af"
                tickFormatter={formatYAxis}
                width={60}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  fontSize: '12px',
                }}
                formatter={(value: any) => [formatter ? formatter(value) : value, label]}
                labelFormatter={(period) => `Year: ${formatPeriod(period)}`}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={chartColor}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Current Value Badge */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500">Current:</span>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${badgeColorClasses[color]}`}>
          {formattedValue}
        </span>
      </div>

      {!hasData && (
        <div className="text-center py-4 text-xs text-gray-400">
          No historical data available
        </div>
      )}
    </div>
  );
}
