import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AppState } from '@/types';

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      selectedTicker: null,
      setSelectedTicker: (ticker) => set({ selectedTicker: ticker }),
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      sectionVisibility: {
        valuation: true,
        profitability: true,
        cash_generation: true,
        financial_strength: true,
        capital_allocation: true,
        moat: true,
      },
      setSectionVisibility: (visibility) => set({ sectionVisibility: visibility }),
    }),
    {
      name: 'app-settings',
      partialize: (state) => ({
        sectionVisibility: state.sectionVisibility,
      }),
    }
  )
);
