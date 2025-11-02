import { Plus, X, Loader2 } from 'lucide-react';
import { useWatchlist, useRemoveTicker } from '@/hooks/useWatchlist';
import { useAppStore } from '@/store/appStore';
import { useState } from 'react';
import { AddTickerModal } from '@/components/stock/AddTickerModal';
import { TickerEntry } from '@/types';

export function Sidebar() {
  const { selectedTicker, setSelectedTicker, sidebarOpen, setSidebarOpen } = useAppStore();
  const { data: watchlist, isLoading } = useWatchlist();
  const removeTicker = useRemoveTicker();
  const [showAddModal, setShowAddModal] = useState(false);

  const handleSelectTicker = (symbol: string) => {
    setSelectedTicker(symbol);
    // Close sidebar on mobile after selection
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  };

  const handleRemove = async (symbol: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const confirmMessage = `Remove ${symbol} from watchlist?\n\nWARNING: This will permanently delete all data for ${symbol}, including:\n• All raw market data\n• All calculated metrics\n• Complete historical data\n\nThis action cannot be undone.`;

    if (confirm(confirmMessage)) {
      await removeTicker.mutateAsync(symbol);
      if (selectedTicker === symbol) {
        // Select first available ticker
        const remaining = watchlist?.tickers.filter((ticker: TickerEntry) => ticker.symbol !== symbol);
        setSelectedTicker(remaining && remaining.length > 0 ? remaining[0].symbol : null);
      }
    }
  };

  if (!sidebarOpen) return null;

  return (
    <>
      {/* Backdrop for mobile */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside className="fixed lg:static inset-y-0 left-0 w-72 bg-white border-r border-gray-200 z-30 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowAddModal(true)}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
            >
              <Plus className="w-4 h-4" />
              Add Ticker
            </button>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden ml-2 p-1 hover:bg-gray-100 rounded"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Ticker List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : watchlist && watchlist.tickers.length > 0 ? (
            <div className="p-2">
              {watchlist.tickers.map((ticker: TickerEntry) => (
                <button
                  key={ticker.symbol}
                  onClick={() => handleSelectTicker(ticker.symbol)}
                  className={`w-full text-left p-3 rounded-md mb-1 group relative ${
                    selectedTicker === ticker.symbol
                      ? 'bg-primary text-white'
                      : 'hover:bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-sm">{ticker.symbol}</div>
                      <div
                        className={`text-xs truncate ${
                          selectedTicker === ticker.symbol ? 'text-blue-100' : 'text-gray-500'
                        }`}
                      >
                        {ticker.name || ticker.symbol}
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleRemove(ticker.symbol, e)}
                      className={`opacity-0 group-hover:opacity-100 p-1 rounded ${
                        selectedTicker === ticker.symbol
                          ? 'hover:bg-blue-700'
                          : 'hover:bg-gray-200'
                      }`}
                      title="Remove from watchlist"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="p-4 text-center text-gray-500 text-sm">
              No stocks in watchlist.
              <br />
              Click "Add Ticker" above to get started.
            </div>
          )}
        </div>
      </aside>

      {/* Add Ticker Modal */}
      <AddTickerModal isOpen={showAddModal} onClose={() => setShowAddModal(false)} />
    </>
  );
}
