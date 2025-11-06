import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { StockHeader } from './components/stock/StockHeader';
import { useAppStore } from './store/appStore';
import { useWatchlist } from './hooks/useWatchlist';
import { useStockMetrics } from './hooks/useStock';
import { ValuationMetrics } from './components/metrics/ValuationMetrics';
import { ProfitabilityMetrics } from './components/metrics/ProfitabilityMetrics';
import { CashGenerationMetrics } from './components/metrics/CashGenerationMetrics';
import { FinancialStrengthMetrics } from './components/metrics/FinancialStrengthMetrics';
import { CapitalAllocationMetrics } from './components/metrics/CapitalAllocationMetrics';
import { MoatMetrics } from './components/metrics/MoatMetrics';
import { useAutoRefresh } from './hooks/useAutoRefresh';
import { useEffect } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const { selectedTicker, setSelectedTicker, sectionVisibility } = useAppStore();
  const { data: watchlist } = useWatchlist();
  const { data: metrics, isLoading, error } = useStockMetrics(selectedTicker);

  // Enable auto-refresh every hour (3600000 ms)
  useAutoRefresh(60 * 60 * 1000, true);

  // Auto-select first ticker if none selected
  useEffect(() => {
    if (!selectedTicker && watchlist && watchlist.tickers.length > 0) {
      setSelectedTicker(watchlist.tickers[0].symbol);
    }
  }, [watchlist, selectedTicker, setSelectedTicker]);

  return (
    <Layout>
      {selectedTicker ? (
        <div className="max-w-7xl mx-auto">
          <StockHeader ticker={selectedTicker} />

          {isLoading && (
            <div className="mt-6 text-center text-gray-500">
              <p>Loading metrics...</p>
            </div>
          )}

          {error && (
            <div className="mt-6 text-center text-red-600">
              <p>Error loading metrics: {error.message}</p>
            </div>
          )}

          {metrics && (
            <div className="mt-6">
              {sectionVisibility.valuation && <ValuationMetrics metrics={metrics.valuation} />}
              {sectionVisibility.profitability && (
                <ProfitabilityMetrics ticker={selectedTicker} metrics={metrics.profitability} />
              )}
              {sectionVisibility.cash_generation && (
                <CashGenerationMetrics ticker={selectedTicker} metrics={metrics.cash_generation} />
              )}
              {sectionVisibility.financial_strength && (
                <FinancialStrengthMetrics metrics={metrics.financial_strength} />
              )}
              {sectionVisibility.capital_allocation && (
                <CapitalAllocationMetrics metrics={metrics.capital_allocation} />
              )}
              {sectionVisibility.moat && <MoatMetrics metrics={metrics.moat} />}
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-center h-96">
          <div className="text-center text-gray-500">
            <p className="text-lg">Select a stock from the watchlist to view analysis</p>
            <p className="text-sm mt-2">Or add a new ticker to get started</p>
          </div>
        </div>
      )}
    </Layout>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
