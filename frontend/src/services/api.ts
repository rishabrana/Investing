import axios from 'axios';
import type {
  Watchlist,
  StockOverview,
  StockMetrics,
  StockHistory,
  AddTickerRequest,
  ValidateTickerRequest,
  RefreshStockRequest,
} from '@/types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Watchlist API
export const watchlistApi = {
  getWatchlist: async (name: string = 'default'): Promise<Watchlist> => {
    const response = await api.get<Watchlist>('/watchlist', { params: { name } });
    return response.data;
  },

  addTicker: async (request: AddTickerRequest): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/watchlist/add', request);
    return response.data;
  },

  removeTicker: async (symbol: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/watchlist/${symbol}`);
    return response.data;
  },

  validateTicker: async (
    request: ValidateTickerRequest
  ): Promise<{ is_valid: boolean; symbol: string; company_name: string | null; error: string | null }> => {
    const response = await api.post('/watchlist/validate', request);
    return response.data;
  },
};

// Stock Data API
export const stockApi = {
  getOverview: async (ticker: string): Promise<StockOverview> => {
    const response = await api.get<StockOverview>(`/stocks/${ticker}/overview`);
    return response.data;
  },

  getMetrics: async (ticker: string, profile: string = 'buffett_core'): Promise<StockMetrics> => {
    const response = await api.get<StockMetrics>(`/stocks/${ticker}/metrics`, {
      params: { profile },
    });
    return response.data;
  },

  getHistory: async (ticker: string, metric: string, years: number = 10): Promise<StockHistory> => {
    const response = await api.get<StockHistory>(`/stocks/${ticker}/history`, {
      params: { metric, years },
    });
    return response.data;
  },

  refreshStock: async (ticker: string, request: RefreshStockRequest = {}): Promise<any> => {
    const response = await api.post(`/stocks/${ticker}/refresh`, request);
    return response.data;
  },

  refreshWatchlist: async (watchlist: string = 'default', force: boolean = false): Promise<any> => {
    const response = await api.post('/stocks/refresh-watchlist', { watchlist, force });
    return response.data;
  },
};

export default api;
