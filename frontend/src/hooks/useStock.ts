import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { stockApi } from '@/services/api';

export function useStockOverview(ticker: string | null) {
  return useQuery({
    queryKey: ['stock', 'overview', ticker],
    queryFn: () => stockApi.getOverview(ticker!),
    enabled: !!ticker,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useStockMetrics(ticker: string | null, profile: string = 'buffett_core') {
  return useQuery({
    queryKey: ['stock', 'metrics', ticker, profile],
    queryFn: () => stockApi.getMetrics(ticker!, profile),
    enabled: !!ticker,
    staleTime: 5 * 60 * 1000,
  });
}

export function useStockHistory(ticker: string | null, metric: string, years: number = 10) {
  return useQuery({
    queryKey: ['stock', 'history', ticker, metric, years],
    queryFn: () => stockApi.getHistory(ticker!, metric, years),
    enabled: !!ticker && !!metric,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useRefreshStock() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ticker, force = false }: { ticker: string; force?: boolean }) =>
      stockApi.refreshStock(ticker, { force }),
    onSuccess: (_, { ticker }) => {
      // Invalidate all queries for this ticker
      queryClient.invalidateQueries({ queryKey: ['stock', 'overview', ticker] });
      queryClient.invalidateQueries({ queryKey: ['stock', 'metrics', ticker] });
      queryClient.invalidateQueries({ queryKey: ['stock', 'history', ticker] });
    },
  });
}
