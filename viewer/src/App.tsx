import React, { useState } from 'react';
import { 
  Menu, 
  Archive,
  Search
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import DecisionView from './components/DecisionView';
import RevocationList from './components/RevocationList';
import StatsView from './components/StatsView';
import type { DecisionIndexItem, Revocation } from './types';

// Data imports
import decisionsIndexData from './data/decisions_index.json';
import revocationsData from './data/all_revocations.json';

type ViewMode = 'decisions' | 'revocations' | 'stats';

const App: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('revocations');
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Cast imports to types
  const decisionsIndex = decisionsIndexData as DecisionIndexItem[];
  const revocations = revocationsData as unknown as Revocation[];

  const handleSelectDecision = (id: string) => {
    setSelectedDecisionId(id);
    setViewMode('decisions');
    if (window.innerWidth < 1024) setIsSidebarOpen(false);
  };

  return (
    <div className="flex h-screen overflow-hidden font-sans selection:bg-archive-red/30 selection:text-white">
      {/* Sidebar */}
      <Sidebar 
        isOpen={isSidebarOpen} 
        viewMode={viewMode}
        setViewMode={setViewMode}
        decisions={decisionsIndex}
        selectedId={selectedDecisionId}
        onSelect={handleSelectDecision}
        searchQuery={searchQuery}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 relative overflow-hidden bg-vault-bg">
        <header className="h-16 border-b border-white/5 bg-vault-sidebar/80 backdrop-blur-md flex items-center justify-between px-8 shrink-0 z-20">
          <div className="flex items-center gap-6 flex-1">
            <button 
              className="p-2 hover:bg-white/5 rounded text-white/40 transition-colors"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <Menu size={20} />
            </button>
            
            <div className="relative max-w-md w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/20" size={16} />
              <input 
                type="text" 
                placeholder={viewMode === 'revocations' ? "檢索名冊內容..." : "調閱卷宗編號..."}
                className="w-full bg-white/5 border border-white/10 py-2 pl-10 pr-4 text-sm text-white focus:ring-1 focus:ring-archive-gold/50 transition-all placeholder:text-white/20 font-serif"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-[10px] font-bold text-archive-gold uppercase tracking-[0.4em] leading-none mb-1">TRANSITIONAL JUSTICE</div>
              <div className="text-[9px] font-mono text-white/30 uppercase tracking-tighter">Official Digital Archive / v.2026</div>
            </div>
            <div className="w-px h-8 bg-white/10 mx-1" />
            <Archive size={20} className="text-white/60" />
          </div>
        </header>

        <div className="flex-1 overflow-auto custom-scrollbar">
          {viewMode === 'decisions' && (
            <DecisionView id={selectedDecisionId} searchQuery={searchQuery} />
          )}
          {viewMode === 'revocations' && (
            <RevocationList 
              revocations={revocations} 
              onSelectDecision={handleSelectDecision} 
              searchTerm={searchQuery}
            />
          )}
          {viewMode === 'stats' && (
            <StatsView decisions={decisionsIndex} revocations={revocations} />
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
