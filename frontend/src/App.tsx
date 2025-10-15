import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { StockHeader } from './components/stock/StockHeader';
import { useAppStore } from './store/appStore';
import { useWatchlist } from './hooks/useWatchlist';
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
  const { selectedTicker, setSelectedTicker } = useAppStore();
  const { data: watchlist } = useWatchlist();

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
          <div className="mt-6 text-center text-gray-500">
            <p>Metric sections coming soon...</p>
            <p className="text-sm mt-2">
              The backend API is working! Frontend components are being built.
            </p>
          </div>
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
