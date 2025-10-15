import { RefreshCw, TrendingUp, TrendingDown } from 'lucide-react';
import { useStockOverview, useRefreshStock } from '@/hooks/useStock';
import { formatCurrency, formatChange, formatDate, getChangeColorClass } from '@/utils/formatters';

interface StockHeaderProps {
  ticker: string;
}

export function StockHeader({ ticker }: StockHeaderProps) {
  const { data: overview, isLoading, error } = useStockOverview(ticker);
  const refreshMutation = useRefreshStock();

  const handleRefresh = () => {
    refreshMutation.mutate({ ticker, force: true });
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 mb-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/3"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
        <p className="text-red-800">Error loading stock data. Try refreshing.</p>
      </div>
    );
  }

  if (!overview) return null;

  const isPositive = (overview.price.change || 0) >= 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        {/* Left side - Stock info */}
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h2 className="text-3xl font-bold text-gray-900">{overview.ticker}</h2>
            <button
              onClick={handleRefresh}
              disabled={refreshMutation.isPending}
              className="p-2 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
              title="Refresh data"
            >
              <RefreshCw
                className={`w-5 h-5 text-gray-600 ${refreshMutation.isPending ? 'animate-spin' : ''}`}
              />
            </button>
          </div>
          <p className="text-gray-600 mt-1">{overview.name || ticker}</p>
          <p className="text-sm text-gray-500 mt-2">As of {formatDate(overview.price.as_of)}</p>
        </div>

        {/* Right side - Price */}
        <div className="text-left sm:text-right">
          <div className="text-4xl font-bold text-gray-900 font-tabular">
            {formatCurrency(overview.price.close)}
          </div>
          {overview.price.change !== null && overview.price.change_percent !== null && (
            <div className={`flex items-center justify-start sm:justify-end gap-1 mt-1 ${getChangeColorClass(overview.price.change)}`}>
              {isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span className="text-lg font-semibold font-tabular">
                {formatChange(overview.price.change)} ({formatChange(overview.price.change_percent)}%)
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Market data */}
      {overview.market_data && (
        <div className="mt-6 pt-4 border-t border-gray-200 grid grid-cols-2 gap-4">
          {overview.market_data.market_cap && (
            <div>
              <p className="text-sm text-gray-500">Market Cap</p>
              <p className="text-lg font-semibold text-gray-900 font-tabular">
                {formatCurrency(overview.market_data.market_cap)}
              </p>
            </div>
          )}
          {overview.market_data.shares_outstanding && (
            <div>
              <p className="text-sm text-gray-500">Shares Outstanding</p>
              <p className="text-lg font-semibold text-gray-900 font-tabular">
                {(overview.market_data.shares_outstanding / 1_000_000_000).toFixed(2)}B
              </p>
            </div>
          )}
        </div>
      )}

      {refreshMutation.isSuccess && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-800">✓ Data refreshed successfully</p>
        </div>
      )}
    </div>
  );
}
