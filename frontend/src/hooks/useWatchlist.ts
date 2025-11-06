import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { watchlistApi, stockApi } from '@/services/api';
import type { AddTickerRequest } from '@/types';

export function useWatchlist(name: string = 'default') {
  return useQuery({
    queryKey: ['watchlist', name],
    queryFn: () => watchlistApi.getWatchlist(name),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useAddTicker() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: AddTickerRequest) => watchlistApi.addTicker(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
    },
  });
}

export function useRemoveTicker() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (symbol: string) => watchlistApi.removeTicker(symbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
    },
  });
}

export function useValidateTicker() {
  return useMutation({
    mutationFn: (symbol: string) => watchlistApi.validateTicker({ symbol }),
  });
}

export function useRefreshAll() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (watchlist: string = 'default') => stockApi.refreshWatchlist(watchlist),
    onSuccess: () => {
      // Invalidate all stock-related queries to refetch fresh data
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
      queryClient.invalidateQueries({ queryKey: ['stock'] });
    },
  });
}
