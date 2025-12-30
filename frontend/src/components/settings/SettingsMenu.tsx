import { Settings, Key, Eye, FileText, Filter, BarChart3 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface SettingsMenuProps {
  onOpenApiKeys: () => void;
  onOpenSectionVisibility: () => void;
  onViewLogs: () => void;
  onViewScreener: () => void;
  onViewMetrics: () => void;
}

export function SettingsMenu({ onOpenApiKeys, onOpenSectionVisibility, onViewLogs, onViewScreener, onViewMetrics }: SettingsMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleMenuItemClick = (action: () => void) => {
    action();
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 hover:bg-gray-100 rounded-md transition-colors"
        aria-label="Settings"
      >
        <Settings className="w-5 h-5 text-gray-700" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
          <button
            onClick={() => handleMenuItemClick(onViewMetrics)}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
          >
            <BarChart3 className="w-4 h-4" />
            Stock Analysis
          </button>
          <button
            onClick={() => handleMenuItemClick(onViewScreener)}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
          >
            <Filter className="w-4 h-4" />
            Value Screener
          </button>
          <div className="border-t border-gray-200 my-1" />
          <button
            onClick={() => handleMenuItemClick(onOpenApiKeys)}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
          >
            <Key className="w-4 h-4" />
            API Keys
          </button>
          <button
            onClick={() => handleMenuItemClick(onOpenSectionVisibility)}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
          >
            <Eye className="w-4 h-4" />
            Section Visibility
          </button>
          <button
            onClick={() => handleMenuItemClick(onViewLogs)}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
          >
            <FileText className="w-4 h-4" />
            View Logs
          </button>
        </div>
      )}
    </div>
  );
}
