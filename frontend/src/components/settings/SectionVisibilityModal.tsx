import { X, Save } from 'lucide-react';
import { useState, useEffect } from 'react';

interface SectionVisibilityModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (visibility: Record<string, boolean>) => void;
  currentVisibility: Record<string, boolean>;
}

const SECTIONS = [
  { id: 'valuation', name: 'Valuation Metrics', description: 'P/E ratio, DCF valuation, margin of safety' },
  { id: 'profitability', name: 'Profitability Metrics', description: 'ROE, ROA, profit margins' },
  { id: 'cash_generation', name: 'Cash Generation', description: 'Free cash flow, owner earnings' },
  { id: 'financial_strength', name: 'Financial Strength', description: 'Debt ratios, interest coverage' },
  { id: 'capital_allocation', name: 'Capital Allocation', description: 'Dividends, buybacks, reinvestment' },
  { id: 'moat', name: 'Economic Moat', description: 'Competitive advantages and sustainability' },
];

export function SectionVisibilityModal({
  isOpen,
  onClose,
  onSave,
  currentVisibility,
}: SectionVisibilityModalProps) {
  const [visibility, setVisibility] = useState<Record<string, boolean>>(currentVisibility);

  useEffect(() => {
    setVisibility(currentVisibility);
  }, [currentVisibility, isOpen]);

  const handleToggle = (sectionId: string) => {
    setVisibility((prev) => ({ ...prev, [sectionId]: !prev[sectionId] }));
  };

  const handleSave = () => {
    onSave(visibility);
    onClose();
  };

  const handleSelectAll = () => {
    const allVisible = SECTIONS.reduce((acc, section) => {
      acc[section.id] = true;
      return acc;
    }, {} as Record<string, boolean>);
    setVisibility(allVisible);
  };

  const handleDeselectAll = () => {
    const allHidden = SECTIONS.reduce((acc, section) => {
      acc[section.id] = false;
      return acc;
    }, {} as Record<string, boolean>);
    setVisibility(allHidden);
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Section Visibility</h2>
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
              Choose which metric sections to display in your analysis. Hidden sections won't be shown but can be re-enabled at any time.
            </p>

            <div className="flex gap-2 mb-4">
              <button
                onClick={handleSelectAll}
                className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Select All
              </button>
              <button
                onClick={handleDeselectAll}
                className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Deselect All
              </button>
            </div>

            <div className="space-y-3">
              {SECTIONS.map((section) => (
                <div
                  key={section.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={visibility[section.id] ?? true}
                      onChange={() => handleToggle(section.id)}
                      className="mt-1 w-4 h-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{section.name}</div>
                      <div className="text-sm text-gray-600">{section.description}</div>
                    </div>
                  </label>
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
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
