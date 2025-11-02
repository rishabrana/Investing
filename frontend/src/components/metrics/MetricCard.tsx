import { ReactNode } from 'react';

interface MetricCardProps {
  label: string;
  value: string | number | null | undefined;
  formatter?: (value: any) => string;
  description?: string;
  color?: 'default' | 'positive' | 'negative' | 'warning';
  icon?: ReactNode;
}

export function MetricCard({
  label,
  value,
  formatter,
  description,
  color = 'default',
  icon,
}: MetricCardProps) {
  const formattedValue = formatter && value !== null && value !== undefined
    ? formatter(value)
    : value?.toString() ?? 'N/A';

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
