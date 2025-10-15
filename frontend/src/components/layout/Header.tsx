import { Menu, RefreshCw } from 'lucide-react';
import { useAppStore } from '@/store/appStore';

export function Header() {
  const { setSidebarOpen, sidebarOpen } = useAppStore();

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden p-2 hover:bg-gray-100 rounded-md"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h1 className="text-xl font-bold text-primary">Investment Analysis</h1>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-sm text-neutral hidden sm:inline">Buffett-Style Analysis</span>
      </div>
    </header>
  );
}
