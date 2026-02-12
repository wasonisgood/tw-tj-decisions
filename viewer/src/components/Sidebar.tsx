import React from 'react';
import { 
  FileText, 
  Users, 
  BarChart3, 
  Search, 
  BookOpen
} from 'lucide-react';
import type { DecisionIndexItem } from '../types';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface SidebarProps {
  isOpen: boolean;
  viewMode: string;
  setViewMode: (mode: any) => void;
  decisions: DecisionIndexItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  searchQuery: string;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  isOpen, 
  viewMode, 
  setViewMode, 
  decisions, 
  selectedId, 
  onSelect,
  searchQuery
}) => {
  const filteredDecisions = decisions.filter(d => 
    d.metadata.case_no?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.metadata.subject?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <aside className={cn(
      "fixed lg:relative z-40 h-full bg-vault-sidebar text-white/40 transition-all duration-300 flex flex-col shrink-0 border-r border-white/5",
      isOpen ? "w-72 translate-x-0" : "w-0 -translate-x-full lg:w-20 lg:translate-x-0"
    )}>
      <div className="p-8 flex items-center gap-4 overflow-hidden">
        <div className="bg-archive-gold p-2 rounded shrink-0">
          <BookOpen className="text-black" size={18} />
        </div>
        <div className={cn("transition-opacity whitespace-nowrap", !isOpen && "lg:opacity-0")}>
          <div className="font-bold text-white tracking-widest text-sm">數位卷宗</div>
          <div className="text-[9px] opacity-40 uppercase tracking-tighter font-mono">Archive Access</div>
        </div>
      </div>

      <nav className="px-4 flex flex-col gap-2">
        <NavItem 
          icon={<Users size={18} />} 
          label="公告名冊" 
          active={viewMode === 'revocations'} 
          onClick={() => setViewMode('revocations')}
          collapsed={!isOpen}
        />
        <NavItem 
          icon={<FileText size={18} />} 
          label="決定書庫" 
          active={viewMode === 'decisions'} 
          onClick={() => setViewMode('decisions')}
          collapsed={!isOpen}
        />
        <NavItem 
          icon={<BarChart3 size={18} />} 
          label="數據解析" 
          active={viewMode === 'stats'} 
          onClick={() => setViewMode('stats')}
          collapsed={!isOpen}
        />
      </nav>

      <div className="mt-12 px-6 mb-4">
        <div className={cn("text-[9px] font-bold uppercase tracking-[0.3em] text-white/20 transition-opacity", !isOpen && "lg:opacity-0")}>
          INDEXED FILES ({filteredDecisions.length})
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 custom-scrollbar">
        {filteredDecisions.map(d => (
          <button
            key={d.id}
            onClick={() => onSelect(d.id)}
            className={cn(
              "w-full text-left py-3 px-4 rounded transition-all flex items-center gap-3 group border-b border-white/5",
              selectedId === d.id ? "bg-white/5 text-archive-gold" : "hover:text-white"
            )}
          >
            <div className={cn(
              "w-1 h-1 rounded-full",
              selectedId === d.id ? "bg-archive-gold" : "bg-white/10"
            )} />
            <div className={cn("transition-opacity duration-300 truncate", !isOpen && "lg:opacity-0")}>
              <div className="text-[9px] opacity-30 font-mono mb-0.5">{d.metadata.case_no}</div>
              <div className="text-xs font-medium truncate tracking-tight">{d.metadata.subject}</div>
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
};

const NavItem = ({ icon, label, active, onClick, collapsed }: any) => (
  <button 
    onClick={onClick}
    className={cn(
      "flex items-center gap-4 p-3 rounded transition-all w-full group",
      active ? "bg-white/5 text-white" : "hover:bg-white/5 text-white/30"
    )}
  >
    <div className={cn("shrink-0", active ? "text-archive-gold" : "")}>{icon}</div>
    <span className={cn("text-xs font-bold transition-all duration-300 whitespace-nowrap tracking-widest", collapsed && "lg:opacity-0 w-0 overflow-hidden")}>
      {label}
    </span>
    {active && !collapsed && <div className="ml-auto w-1 h-1 bg-archive-gold rounded-full" />}
  </button>
);

export default Sidebar;
