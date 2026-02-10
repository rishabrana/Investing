import { useState } from 'react';
import { watchlistApi, stockApi } from '@/services/api';
import { useQueryClient } from '@tanstack/react-query';
import { useAppStore } from '@/store/appStore';
import type { ValidateTickerResult } from '@/types';

interface AddTickerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type FlowStep = 'input' | 'validating' | 'confirmed' | 'processing' | 'success' | 'error';

interface ProcessingStatus {
  symbol: string;
  status: 'pending' | 'adding' | 'fetching' | 'done' | 'error';
  error?: string;
}

export function AddTickerModal({ isOpen, onClose }: AddTickerModalProps) {
  const [input, setInput] = useState('');
  const [validationResults, setValidationResults] = useState<ValidateTickerResult[]>([]);
  const [step, setStep] = useState<FlowStep>('input');
  const [error, setError] = useState<string | null>(null);
  const [processingStatuses, setProcessingStatuses] = useState<ProcessingStatus[]>([]);
  const [successCount, setSuccessCount] = useState(0);
  const [validatingIndex, setValidatingIndex] = useState(0);
  const [validatingTotal, setValidatingTotal] = useState(0);
  const queryClient = useQueryClient();
  const { setSelectedTicker } = useAppStore();

  if (!isOpen) return null;

  const parseSymbols = (text: string): string[] => {
    return [...new Set(
      text
        .split(',')
        .map(s => s.trim().toUpperCase())
        .filter(s => s.length > 0)
    )];
  };

  const handleValidate = async () => {
    const symbols = parseSymbols(input);

    if (symbols.length === 0) {
      setError('Please enter at least one stock symbol');
      return;
    }

    setStep('validating');
    setError(null);
    setValidationResults([]);
    setValidatingTotal(symbols.length);
    setValidatingIndex(0);

    try {
      // Validate one at a time so UI shows per-symbol progress
      const results: ValidateTickerResult[] = [];

      for (let i = 0; i < symbols.length; i++) {
        setValidatingIndex(i);

        const response = await watchlistApi.validateTicker({ symbol: symbols[i] });
        results.push(response);
        setValidationResults([...results]);
      }

      setValidatingIndex(symbols.length);
      const validCount = results.filter(r => r.is_valid).length;

      if (validCount === 0) {
        setError('No valid ticker symbols found. Check your symbols and try again.');
        setStep('error');
      } else {
        setStep('confirmed');
      }
    } catch (err: any) {
      // Even if the batch call fails, show any results we already have
      if (validationResults.length > 0 && validationResults.some(r => r.is_valid)) {
        setStep('confirmed');
      } else {
        setError(err.response?.data?.detail || 'Failed to validate tickers');
        setStep('error');
      }
    }
  };

  const handleAdd = async () => {
    // Only add new valid symbols (skip duplicates)
    const newSymbols = validationResults.filter(
      r => r.is_valid && r.error !== 'already_in_watchlist'
    );

    if (newSymbols.length === 0) {
      setError('No new tickers to add');
      return;
    }

    setStep('processing');
    setError(null);
    setSuccessCount(0);

    const initialStatuses: ProcessingStatus[] = newSymbols.map(r => ({
      symbol: r.symbol,
      status: 'pending',
    }));
    setProcessingStatuses(initialStatuses);

    let completed = 0;
    let lastSuccessfulSymbol = '';

    for (let i = 0; i < newSymbols.length; i++) {
      const { symbol, company_name } = newSymbols[i];

      setProcessingStatuses(prev => prev.map((s, idx) =>
        idx === i ? { ...s, status: 'adding' } : s
      ));

      try {
        await watchlistApi.addTicker({
          symbol,
          name: company_name || undefined,
        });

        setProcessingStatuses(prev => prev.map((s, idx) =>
          idx === i ? { ...s, status: 'fetching' } : s
        ));

        await stockApi.refreshStock(symbol, { force: true });

        setProcessingStatuses(prev => prev.map((s, idx) =>
          idx === i ? { ...s, status: 'done' } : s
        ));

        completed++;
        lastSuccessfulSymbol = symbol;
        setSuccessCount(completed);

      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || err.message || 'Failed';
        setProcessingStatuses(prev => prev.map((s, idx) =>
          idx === i ? { ...s, status: 'error', error: errorMsg } : s
        ));
      }
    }

    queryClient.invalidateQueries({ queryKey: ['watchlist'] });
    newSymbols.forEach(({ symbol }) => {
      queryClient.invalidateQueries({ queryKey: ['stock', 'overview', symbol] });
      queryClient.invalidateQueries({ queryKey: ['stock', 'metrics', symbol] });
    });

    if (lastSuccessfulSymbol) {
      setSelectedTicker(lastSuccessfulSymbol);
    }

    setStep('success');
  };

  const handleClose = () => {
    setInput('');
    setValidationResults([]);
    setStep('input');
    setError(null);
    setProcessingStatuses([]);
    setSuccessCount(0);
    setValidatingIndex(0);
    setValidatingTotal(0);
    onClose();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && step === 'input') {
      handleValidate();
    }
  };

  const validCount = validationResults.filter(r => r.is_valid).length;
  const invalidCount = validationResults.filter(r => !r.is_valid).length;
  const duplicateCount = validationResults.filter(r => r.error === 'already_in_watchlist').length;
  const newValidCount = validCount - duplicateCount;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 flex-shrink-0">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Add Stocks to Watchlist</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600"
              disabled={step === 'processing'}
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
                <label htmlFor="symbols" className="block text-sm font-medium text-gray-700 mb-2">
                  Stock Symbols
                </label>
                <input
                  id="symbols"
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value.toUpperCase())}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g., AAPL, MSFT, GOOGL"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  autoFocus
                />
                <p className="mt-2 text-sm text-gray-500">
                  Enter one or more symbols separated by commas
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleValidate}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Validate Symbols
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

          {/* Validating Step - per-symbol progress */}
          {step === 'validating' && (
            <div className="py-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm text-gray-600">
                  Validating {Math.min(validatingIndex + 1, validatingTotal)} of {validatingTotal} symbols...
                </p>
                {validatingIndex < validatingTotal && (
                  <span className="text-sm font-medium text-blue-600 flex items-center">
                    <span className="animate-spin h-3 w-3 border-b-2 border-blue-600 rounded-full mr-2"></span>
                    {parseSymbols(input)[validatingIndex]}
                  </span>
                )}
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${validatingTotal > 0 ? (validatingIndex / validatingTotal) * 100 : 0}%` }}
                ></div>
              </div>

              {/* Already-validated results */}
              {validationResults.length > 0 && (
                <div className="space-y-1 max-h-40 overflow-y-auto">
                  {validationResults.map((result, idx) => (
                    <div key={idx} className="flex items-center text-sm py-1">
                      {result.is_valid ? (
                        <svg className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4 text-red-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      )}
                      <span className="font-medium mr-2">{result.symbol}</span>
                      {result.is_valid && result.company_name && (
                        <span className="text-gray-500 truncate">{result.company_name}</span>
                      )}
                      {result.error === 'already_in_watchlist' && (
                        <span className="text-amber-600 text-xs ml-1">(already added)</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Confirmed Step - scrollable results */}
        {step === 'confirmed' && (
          <>
            <div className="px-6 flex-shrink-0">
              <div className="flex gap-4 mb-4">
                {newValidCount > 0 && (
                  <div className="flex items-center text-sm">
                    <span className="w-3 h-3 rounded-full bg-green-500 mr-2"></span>
                    <span className="text-gray-600">{newValidCount} valid</span>
                  </div>
                )}
                {duplicateCount > 0 && (
                  <div className="flex items-center text-sm">
                    <span className="w-3 h-3 rounded-full bg-amber-400 mr-2"></span>
                    <span className="text-gray-600">{duplicateCount} already added</span>
                  </div>
                )}
                {invalidCount > 0 && (
                  <div className="flex items-center text-sm">
                    <span className="w-3 h-3 rounded-full bg-red-500 mr-2"></span>
                    <span className="text-gray-600">{invalidCount} invalid</span>
                  </div>
                )}
              </div>
            </div>

            <div className="px-6 overflow-y-auto flex-1 max-h-60">
              <div className="space-y-2">
                {validationResults.map((result, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border ${
                      result.error === 'already_in_watchlist'
                        ? 'bg-amber-50 border-amber-200'
                        : result.is_valid
                        ? 'bg-green-50 border-green-200'
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        {result.error === 'already_in_watchlist' ? (
                          <svg className="w-5 h-5 text-amber-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                          </svg>
                        ) : result.is_valid ? (
                          <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                          </svg>
                        )}
                        <span className={`font-semibold ${
                          result.error === 'already_in_watchlist'
                            ? 'text-amber-900'
                            : result.is_valid ? 'text-green-900' : 'text-red-900'
                        }`}>
                          {result.symbol}
                        </span>
                      </div>
                    </div>
                    {result.error === 'already_in_watchlist' && (
                      <p className="text-sm text-amber-700 ml-7">Already in your watchlist (skipped)</p>
                    )}
                    {result.is_valid && result.error !== 'already_in_watchlist' && result.company_name && (
                      <p className="text-sm text-green-700 ml-7">{result.company_name}</p>
                    )}
                    {!result.is_valid && result.error && (
                      <p className="text-sm text-red-700 ml-7">{result.error}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 flex-shrink-0 border-t">
              <p className="text-sm text-gray-600 mb-4">
                {newValidCount > 0
                  ? `${newValidCount} new ticker${newValidCount !== 1 ? 's' : ''} will be added and data will be fetched.`
                  : 'All symbols are already in your watchlist.'}
                {duplicateCount > 0 && newValidCount > 0 && ` (${duplicateCount} duplicate${duplicateCount !== 1 ? 's' : ''} skipped)`}
              </p>
              <div className="flex gap-3">
                <button
                  onClick={handleAdd}
                  disabled={newValidCount === 0}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {newValidCount > 0
                    ? `Add ${newValidCount} Stock${newValidCount !== 1 ? 's' : ''} & Fetch Data`
                    : 'Nothing to Add'}
                </button>
                <button
                  onClick={() => setStep('input')}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Back
                </button>
              </div>
            </div>
          </>
        )}

        {/* Processing Step */}
        {step === 'processing' && (
          <>
            <div className="px-6 flex-shrink-0">
              <p className="text-sm text-gray-600 mb-4">
                Processing {successCount} of {processingStatuses.length} stocks...
              </p>
            </div>
            <div className="px-6 overflow-y-auto flex-1 max-h-60">
              <div className="space-y-2">
                {processingStatuses.map((status, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border ${
                      status.status === 'done'
                        ? 'bg-green-50 border-green-200'
                        : status.status === 'error'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-gray-900">{status.symbol}</span>
                      <span className="text-sm">
                        {status.status === 'pending' && (
                          <span className="text-gray-500">Waiting...</span>
                        )}
                        {status.status === 'adding' && (
                          <span className="text-blue-600 flex items-center">
                            <span className="animate-spin h-4 w-4 border-b-2 border-blue-600 rounded-full mr-2"></span>
                            Adding...
                          </span>
                        )}
                        {status.status === 'fetching' && (
                          <span className="text-blue-600 flex items-center">
                            <span className="animate-spin h-4 w-4 border-b-2 border-blue-600 rounded-full mr-2"></span>
                            Fetching data...
                          </span>
                        )}
                        {status.status === 'done' && (
                          <span className="text-green-600 flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            Done
                          </span>
                        )}
                        {status.status === 'error' && (
                          <span className="text-red-600 flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            Failed
                          </span>
                        )}
                      </span>
                    </div>
                    {status.error && (
                      <p className="text-sm text-red-600 mt-1">{status.error}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="p-6 flex-shrink-0 border-t">
              <p className="text-sm text-gray-500">Please wait while stocks are being added...</p>
            </div>
          </>
        )}

        {/* Success Step */}
        {step === 'success' && (
          <div className="p-6">
            <div className="text-center py-4">
              <div className="inline-block rounded-full bg-green-100 p-3 mb-4">
                <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-green-900 font-semibold mb-1">Complete!</p>
              <p className="text-sm text-gray-600 mb-4">
                {successCount} of {processingStatuses.length} stock{processingStatuses.length !== 1 ? 's' : ''} added successfully
              </p>
              <button
                onClick={handleClose}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Error Step */}
        {step === 'error' && (
          <div className="p-6">
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
          </div>
        )}
      </div>
    </div>
  );
}
