import { ReactNode } from 'react';
import { InfoIcon } from '@/components/common/InfoIcon';
import { getMetricInfo } from '@/utils/metricInfo';

interface MetricCardProps {
  label: string;
  value: string | number | null | undefined;
  formatter?: (value: any) => string;
  description?: string;
  color?: 'default' | 'positive' | 'negative' | 'warning';
  icon?: ReactNode;
  metricKey?: string; // Used to lookup info from metricInfoMap
  infoDescription?: string; // Override default description
  infoUrl?: string; // Override default learn more URL
}

export function MetricCard({
  label,
  value,
  formatter,
  description,
  color = 'default',
  icon,
  metricKey,
  infoDescription,
  infoUrl,
}: MetricCardProps) {
  const formattedValue = formatter && value !== null && value !== undefined
    ? formatter(value)
    : value?.toString() ?? 'N/A';

  // Get metric info from the map or use overrides
  const metricInfo = metricKey ? getMetricInfo(metricKey) : undefined;
  const tooltipDescription = infoDescription || metricInfo?.description;
  const tooltipUrl = infoUrl || metricInfo?.learnMoreUrl;

  const colorClasses = {
    default: 'text-gray-900',
    positive: 'text-green-600',
    negative: 'text-red-600',
    warning: 'text-yellow-600',
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
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
          <p className={`text-2xl font-semibold mt-2 ${colorClasses[color]}`}>
            {formattedValue}
          </p>
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
      </div>
    </div>
  );
}
