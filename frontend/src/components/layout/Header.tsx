import { Menu } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { SettingsMenu } from '@/components/settings/SettingsMenu';
import { ApiKeysModal } from '@/components/settings/ApiKeysModal';
import { SectionVisibilityModal } from '@/components/settings/SectionVisibilityModal';
import { useState } from 'react';

export function Header() {
  const { setSidebarOpen, sidebarOpen, sectionVisibility, setSectionVisibility, setViewMode } = useAppStore();
  const [showApiKeysModal, setShowApiKeysModal] = useState(false);
  const [showSectionVisibilityModal, setShowSectionVisibilityModal] = useState(false);

  const handleViewLogs = () => {
    setViewMode('logs');
  };

  const handleViewScreener = () => {
    setViewMode('screener');
  };

  const handleViewMetrics = () => {
    setViewMode('metrics');
  };

  return (
    <>
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5 text-gray-700" />
          </button>
          <h1 className="text-xl font-bold text-primary">Investment Analysis</h1>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-neutral hidden sm:inline">Buffett-Style Analysis</span>
          <SettingsMenu
            onOpenApiKeys={() => setShowApiKeysModal(true)}
            onOpenSectionVisibility={() => setShowSectionVisibilityModal(true)}
            onViewLogs={handleViewLogs}
            onViewScreener={handleViewScreener}
            onViewMetrics={handleViewMetrics}
          />
        </div>
      </header>

      <ApiKeysModal isOpen={showApiKeysModal} onClose={() => setShowApiKeysModal(false)} />
      <SectionVisibilityModal
        isOpen={showSectionVisibilityModal}
        onClose={() => setShowSectionVisibilityModal(false)}
        onSave={setSectionVisibility}
        currentVisibility={sectionVisibility}
      />
    </>
  );
}
