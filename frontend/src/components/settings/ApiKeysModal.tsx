import { X, Eye, EyeOff, Save, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';

interface ApiKeysModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ApiKey {
  provider: string;
  displayName: string;
  value: string;
  isNew: boolean;
}

const API_PROVIDERS = [
  { id: 'polygon.io', name: 'Polygon.io', envVar: 'POLYGON_API_KEY' },
  { id: 'financial_modeling_prep', name: 'Financial Modeling Prep', envVar: 'FMP_API_KEY' },
  { id: 'alpha_vantage', name: 'Alpha Vantage', envVar: 'ALPHA_VANTAGE_API_KEY' },
  { id: 'finnhub.io', name: 'Finnhub.io', envVar: 'FINNHUB_API_KEY' },
];

export function ApiKeysModal({ isOpen, onClose }: ApiKeysModalProps) {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadApiKeys();
    }
  }, [isOpen]);

  const loadApiKeys = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/settings/api-keys');
      if (response.ok) {
        const data = await response.json();
        const keys = API_PROVIDERS.map((provider) => ({
          provider: provider.id,
          displayName: provider.name,
          value: data[provider.id] || '',
          isNew: !data[provider.id],
        }));
        setApiKeys(keys);
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
      // Initialize with empty values
      const keys = API_PROVIDERS.map((provider) => ({
        provider: provider.id,
        displayName: provider.name,
        value: '',
        isNew: true,
      }));
      setApiKeys(keys);
    }
  };

  const handleKeyChange = (provider: string, value: string) => {
    setApiKeys((prev) =>
      prev.map((key) =>
        key.provider === provider ? { ...key, value, isNew: !value } : key
      )
    );
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const keysToSave = apiKeys.reduce((acc, key) => {
        if (key.value) {
          acc[key.provider] = key.value;
        }
        return acc;
      }, {} as Record<string, string>);

      const response = await fetch('http://localhost:8000/api/settings/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keysToSave),
      });

      if (response.ok) {
        alert('API keys saved successfully!');
        onClose();
      } else {
        alert('Failed to save API keys');
      }
    } catch (error) {
      console.error('Failed to save API keys:', error);
      alert('Failed to save API keys');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (provider: string) => {
    if (!confirm(`Delete API key for ${apiKeys.find((k) => k.provider === provider)?.displayName}?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/settings/api-keys/${provider}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setApiKeys((prev) =>
          prev.map((key) =>
            key.provider === provider ? { ...key, value: '', isNew: true } : key
          )
        );
      } else {
        alert('Failed to delete API key');
      }
    } catch (error) {
      console.error('Failed to delete API key:', error);
      alert('Failed to delete API key');
    }
  };

  const toggleShowKey = (provider: string) => {
    setShowKeys((prev) => ({ ...prev, [provider]: !prev[provider] }));
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">API Keys</h2>
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            <p className="text-sm text-gray-600 mb-4">
              Configure API keys for stock data providers. These keys are stored locally and used to fetch market data.
            </p>

            <div className="space-y-4">
              {apiKeys.map((apiKey) => (
                <div key={apiKey.provider} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      {apiKey.displayName}
                    </label>
                    {!apiKey.isNew && apiKey.value && (
                      <button
                        onClick={() => handleDelete(apiKey.provider)}
                        className="text-red-600 hover:text-red-700 p-1"
                        title="Delete API key"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  <div className="relative">
                    <input
                      type={showKeys[apiKey.provider] ? 'text' : 'password'}
                      value={apiKey.value}
                      onChange={(e) => handleKeyChange(apiKey.provider, e.target.value)}
                      placeholder="Enter API key"
                      className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                    <button
                      type="button"
                      onClick={() => toggleShowKey(apiKey.provider)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 rounded"
                    >
                      {showKeys[apiKey.provider] ? (
                        <EyeOff className="w-4 h-4 text-gray-500" />
                      ) : (
                        <Eye className="w-4 h-4 text-gray-500" />
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
