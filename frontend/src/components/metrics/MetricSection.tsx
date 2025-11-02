import { ReactNode } from 'react';

interface MetricSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
  icon?: ReactNode;
}

export function MetricSection({
  title,
  description,
  children,
  icon,
}: MetricSectionProps) {
  return (
    <div className="bg-gray-50 rounded-lg p-6 mb-6">
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1">
          {icon && <span className="text-gray-500">{icon}</span>}
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
        </div>
        {description && (
          <p className="text-sm text-gray-600">{description}</p>
        )}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {children}
      </div>
    </div>
  );
}
