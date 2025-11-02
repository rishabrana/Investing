import { useState } from 'react';
import { watchlistApi, stockApi } from '@/services/api';
import { useQueryClient } from '@tanstack/react-query';
import { useAppStore } from '@/store/appStore';

interface AddTickerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type FlowStep = 'input' | 'validating' | 'confirmed' | 'adding' | 'fetching' | 'calculating' | 'success' | 'error';

export function AddTickerModal({ isOpen, onClose }: AddTickerModalProps) {
  const [symbol, setSymbol] = useState('');
  const [companyName, setCompanyName] = useState<string | null>(null);
  const [step, setStep] = useState<FlowStep>('input');
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<string>('');
  const queryClient = useQueryClient();
  const { setSelectedTicker } = useAppStore();

  if (!isOpen) return null;

  const handleValidate = async () => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setStep('validating');
    setError(null);

    try {
      const result = await watchlistApi.validateTicker({ symbol: symbol.trim().toUpperCase() });

      if (result.is_valid) {
        setSymbol(result.symbol);
        setCompanyName(result.company_name);
        setStep('confirmed');
      } else {
        setError(result.error || 'Invalid ticker symbol');
        setStep('error');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to validate ticker');
      setStep('error');
    }
  };

  const handleAdd = async () => {
    setStep('adding');
    setError(null);
    setProgress('Adding ticker to watchlist...');

    try {
      // Step 1: Add to watchlist
      await watchlistApi.addTicker({
        symbol: symbol.toUpperCase(),
        name: companyName || undefined,
      });

      // Step 2: Fetch data
      setStep('fetching');
      setProgress('Fetching stock data from API...');
      await stockApi.refreshStock(symbol.toUpperCase(), { force: true });

      // Step 3: Calculate metrics (this happens automatically on the backend after refresh)
      setStep('calculating');
      setProgress('Calculating metrics...');

      // Wait a bit for metrics to be calculated
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 4: Success - invalidate queries and select the new ticker
      setStep('success');
      setProgress('Complete!');

      // Invalidate all relevant queries to force refresh
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
      queryClient.invalidateQueries({ queryKey: ['stock', 'overview', symbol.toUpperCase()] });
      queryClient.invalidateQueries({ queryKey: ['stock', 'metrics', symbol.toUpperCase()] });

      // Select the newly added ticker
      setSelectedTicker(symbol.toUpperCase());

      // Close modal after a short delay
      setTimeout(() => {
        handleClose();
      }, 1500);

    } catch (err: any) {
      console.error('Error adding ticker:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to add ticker');
      setStep('error');
    }
  };

  const handleClose = () => {
    setSymbol('');
    setCompanyName(null);
    setStep('input');
    setError(null);
    setProgress('');
    onClose();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && step === 'input') {
      handleValidate();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Add Stock to Watchlist</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600"
              disabled={step === 'adding' || step === 'fetching' || step === 'calculating'}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Input Step */}
          {step === 'input' && (
            <>
              <div className="mb-4">
                <label htmlFor="symbol" className="block text-sm font-medium text-gray-700 mb-2">
                  Stock Symbol
                </label>
                <input
                  id="symbol"
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g., AAPL, MSFT, GOOGL"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  autoFocus
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleValidate}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Validate Symbol
                </button>
                <button
                  onClick={handleClose}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </>
          )}

          {/* Validating Step */}
          {step === 'validating' && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-gray-600">Validating ticker symbol...</p>
            </div>
          )}

          {/* Confirmed Step */}
          {step === 'confirmed' && (
            <>
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-green-600 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="font-semibold text-green-900">{symbol}</p>
                    {companyName && <p className="text-sm text-green-700">{companyName}</p>}
                  </div>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                This will add the ticker to your watchlist, fetch the latest data, and calculate all metrics.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={handleAdd}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Add & Fetch Data
                </button>
                <button
                  onClick={() => setStep('input')}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Back
                </button>
              </div>
            </>
          )}

          {/* Processing Steps */}
          {(step === 'adding' || step === 'fetching' || step === 'calculating') && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-gray-900 font-medium mb-2">{progress}</p>
              <p className="text-sm text-gray-500">This may take a few moments...</p>
            </div>
          )}

          {/* Success Step */}
          {step === 'success' && (
            <div className="text-center py-8">
              <div className="inline-block rounded-full bg-green-100 p-3 mb-4">
                <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-green-900 font-semibold mb-1">Successfully Added!</p>
              <p className="text-sm text-gray-600">{symbol} has been added to your watchlist</p>
            </div>
          )}

          {/* Error Step */}
          {step === 'error' && (
            <>
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-red-600 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="font-semibold text-red-900">Error</p>
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setStep('input')}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Try Again
                </button>
                <button
                  onClick={handleClose}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
