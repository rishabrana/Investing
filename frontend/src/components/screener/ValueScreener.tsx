import { useQuery } from '@tanstack/react-query';
import { getValueScreener } from '@/services/api';
import { Loader2, TrendingUp, TrendingDown, Award, CheckCircle2, XCircle } from 'lucide-react';
import type { ScreenedStock } from '@/types';

export function ValueScreener() {
  const { data: screenerData, isLoading, error } = useQuery({
    queryKey: ['value-screener'],
    queryFn: getValueScreener,
    refetchOnMount: true,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600">Error loading screener: {error.message}</p>
      </div>
    );
  }

  if (!screenerData || screenerData.stocks.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-500">No stocks in watchlist to screen.</p>
        <p className="text-sm text-gray-400 mt-2">Add stocks to your watchlist to see them ranked here.</p>
      </div>
    );
  }

  const formatValue = (value: number | null, format: 'percent' | 'ratio' | 'number' | 'currency' = 'number'): string => {
    if (value === null || value === undefined) return 'N/A';

    switch (format) {
      case 'percent':
        return `${(value * 100).toFixed(1)}%`;
      case 'ratio':
        return value.toFixed(2);
      case 'currency':
        if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
        if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
        if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
        return `$${value.toFixed(0)}`;
      default:
        return value.toFixed(2);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-blue-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-50';
    if (score >= 0.6) return 'bg-blue-50';
    if (score >= 0.4) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 0.8) return 'Strong Buy';
    if (score >= 0.6) return 'Buy';
    if (score >= 0.4) return 'Hold';
    return 'Avoid';
  };

  const getRankIcon = (index: number) => {
    if (index === 0) return <Award className="w-5 h-5 text-yellow-500" />;
    if (index === 1) return <Award className="w-5 h-5 text-gray-400" />;
    if (index === 2) return <Award className="w-5 h-5 text-amber-600" />;
    return null;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Value Investing Screener</h1>
        <p className="text-gray-600 mt-2">
          Stocks ranked by fundamental value metrics
        </p>
        <div className="text-sm text-gray-500 mt-1">
          Screened {screenerData.stocks.length} stocks using {screenerData.criteria_count} criteria • Last updated:{' '}
          {new Date(screenerData.screened_at).toLocaleString()}
        </div>
      </div>

      <div className="space-y-4">
        {screenerData.stocks.map((stock: ScreenedStock, index: number) => (
          <div
            key={stock.ticker}
            className={`bg-white rounded-lg border-2 ${
              index === 0 ? 'border-yellow-400' : 'border-gray-200'
            } shadow-sm hover:shadow-md transition-shadow`}
          >
            {/* Stock Header */}
            <div className="p-5 border-b border-gray-100">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 font-bold text-gray-700">
                    {getRankIcon(index) || `#${index + 1}`}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-xl font-bold text-gray-900">{stock.ticker}</h3>
                      {stock.price && (
                        <span className="text-lg text-gray-600">${stock.price.toFixed(2)}</span>
                      )}
                    </div>
                    {stock.name && <p className="text-sm text-gray-500">{stock.name}</p>}
                    {stock.market_cap && (
                      <p className="text-xs text-gray-400 mt-1">
                        Market Cap: {formatValue(stock.market_cap, 'currency')}
                      </p>
                    )}
                  </div>
                </div>

                {/* Overall Score */}
                <div className={`text-center px-6 py-3 rounded-lg ${getScoreBgColor(stock.overall_score)}`}>
                  <div className={`text-3xl font-bold ${getScoreColor(stock.overall_score)}`}>
                    {(stock.overall_score * 100).toFixed(0)}
                  </div>
                  <div className={`text-xs font-semibold ${getScoreColor(stock.overall_score)}`}>
                    {getScoreLabel(stock.overall_score)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {stock.total_points}/{stock.max_points} points
                  </div>
                </div>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="p-5">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {stock.scores.map((scoreData, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-md border ${
                      scoreData.passes ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="text-xs font-medium text-gray-700 uppercase">
                          {scoreData.metric_name}
                        </div>
                        <div className="text-lg font-bold text-gray-900 mt-1">
                          {scoreData.value !== null ? scoreData.value.toFixed(2) : 'N/A'}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">Target: {scoreData.target}</div>
                      </div>
                      <div className="flex flex-col items-end">
                        {scoreData.passes ? (
                          <CheckCircle2 className="w-5 h-5 text-green-600" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-600" />
                        )}
                        <div className="text-xs font-semibold text-gray-600 mt-1">
                          {(scoreData.score * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
