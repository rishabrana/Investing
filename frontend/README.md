# Investment Analysis Frontend

React + TypeScript + Vite frontend for the Investment Analysis web application.

## Status: Partially Implemented

### ✅ Completed
- Project structure and configuration
- TypeScript types and interfaces
- API client with axios
- React Query hooks for data fetching
- Zustand store for app state
- Utility functions for formatting
- Header and Sidebar layout components

### 🚧 To Complete
1. Stock header component
2. Metric card components
3. Metric sections for each category
4. Charts with Recharts
5. Main App component
6. CSS styles (Tailwind)
7. Add ticker modal
8. Loading and error states

## Installation

```bash
cd frontend
npm install
```

## Running the App

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx           ✅ Done
│   │   ├── Sidebar.tsx          ✅ Done
│   │   └── Layout.tsx           🚧 To create
│   ├── stock/
│   │   └── StockHeader.tsx      🚧 To create
│   ├── metrics/
│   │   ├── MetricCard.tsx       🚧 To create
│   │   ├── MetricSection.tsx    🚧 To create
│   │   └── MetricChart.tsx      🚧 To create
│   └── watchlist/
│       └── AddTickerModal.tsx   🚧 To create
├── hooks/
│   ├── useWatchlist.ts          ✅ Done
│   └── useStock.ts              ✅ Done
├── services/
│   └── api.ts                   ✅ Done
├── store/
│   └── appStore.ts              ✅ Done
├── types/
│   └── index.ts                 ✅ Done
├── utils/
│   └── formatters.ts            ✅ Done
├── styles/
│   └── index.css                🚧 To create
├── App.tsx                      🚧 To create
└── main.tsx                     🚧 To create
```

## Next Steps to Complete Frontend

### 1. Create Layout Component

Create `src/components/layout/Layout.tsx`:

```tsx
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

### 2. Create Stock Header Component

Create `src/components/stock/StockHeader.tsx`:

```tsx
import { RefreshCw } from 'lucide-react';
import { useStockOverview } from '@/hooks/useStock';
import { formatCurrency, formatChange, getChangeColorClass } from '@/utils/formatters';

export function StockHeader({ ticker }: { ticker: string }) {
  const { data: overview, isLoading } = useStockOverview(ticker);

  if (isLoading) return <div>Loading...</div>;
  if (!overview) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">{overview.ticker}</h2>
          <p className="text-gray-600">{overview.name}</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold">{formatCurrency(overview.price.close)}</div>
          <div className={`text-sm ${getChangeColorClass(overview.price.change_percent)}`}>
            {formatChange(overview.price.change)} ({formatChange(overview.price.change_percent)}%)
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 3. Create Main App and Entry Point

Create `src/App.tsx`:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { StockHeader } from './components/stock/StockHeader';
import { useAppStore } from './store/appStore';
import { useWatchlist } from './hooks/useWatchlist';
import { useEffect } from 'react';

const queryClient = new QueryClient();

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
        <>
          <StockHeader ticker={selectedTicker} />
          {/* Add metric sections here */}
        </>
      ) : (
        <div className="text-center text-gray-500 mt-20">
          <p>Select a stock from the watchlist to view analysis</p>
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
```

Create `src/main.tsx`:

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### 4. Create Tailwind CSS Entry Point

Create `src/styles/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply font-sans antialiased;
  }
}

@layer utilities {
  .font-tabular {
    font-variant-numeric: tabular-nums;
  }
}
```

### 5. Create index.html

Create `index.html` in frontend root:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Investment Analysis</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## Running Both Backend and Frontend

Terminal 1 - Backend:
```bash
python3 -m backend.api.main
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173

## Features Implemented

- ✅ Watchlist sidebar with add/remove
- ✅ Stock overview with price
- ✅ API integration with React Query
- ✅ Responsive layout (mobile + desktop)
- ✅ Type-safe TypeScript
- ✅ Tailwind CSS styling

## Features To Add

- Metric cards for all 7 categories
- Historical charts with Recharts
- Add ticker modal with validation
- Loading skeletons
- Error boundaries
- Refresh button functionality
- Mobile navigation improvements
