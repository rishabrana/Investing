import { useQuery } from '@tanstack/react-query';
import { logsApi } from '@/services/api';
import type { LogsResponse } from '@/types';

export function useLogs(
  ticker?: string,
  operationType?: string,
  hours: number = 168,
  enabled: boolean = true
) {
  return useQuery<LogsResponse>({
    queryKey: ['logs', ticker, operationType, hours],
    queryFn: () => logsApi.getRecentErrors(ticker, operationType, hours),
    enabled,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}
