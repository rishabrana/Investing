import { useEffect, useRef } from 'react';
import { useRefreshAll } from './useWatchlist';

/**
 * Auto-refresh hook that periodically refreshes all watchlist data
 * @param intervalMs - Refresh interval in milliseconds (default: 1 hour)
 * @param enabled - Whether auto-refresh is enabled (default: true)
 */
export function useAutoRefresh(intervalMs: number = 60 * 60 * 1000, enabled: boolean = true) {
  const refreshAll = useRefreshAll();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    // Set up the interval
    intervalRef.current = setInterval(() => {
      console.log('[AutoRefresh] Triggering scheduled refresh');
      refreshAll.mutate();
    }, intervalMs);

    // Cleanup on unmount or when dependencies change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [intervalMs, enabled, refreshAll]);

  return {
    isRefreshing: refreshAll.isPending,
    lastRefreshSuccess: refreshAll.isSuccess,
    lastRefreshError: refreshAll.error,
  };
}
