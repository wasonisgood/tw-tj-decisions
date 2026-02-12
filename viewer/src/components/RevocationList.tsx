import React, { useState, useMemo } from 'react';
import type { Revocation } from '../types';
import { 
  ExternalLink, 
  ChevronLeft, 
  ChevronRight,
  Filter
} from 'lucide-react';

interface RevocationListProps {
  revocations: Revocation[];
  onSelectDecision: (id: string) => void;
  searchTerm: string;
}

const PAGE_SIZE = 15;

const RevocationList: React.FC<RevocationListProps> = ({ revocations, onSelectDecision, searchTerm }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [categoryFilter, setCategoryFilter] = useState<number | null>(null);

  const filteredData = useMemo(() => {
    return revocations.filter(item => {
      const name = item.name || '';
      const caseId = Array.isArray(item.case_id) ? item.case_id.join('') : (item.case_id || '');
      
      const matchesSearch = 
        name.includes(searchTerm) || 
        caseId.includes(searchTerm);
      const matchesCategory = categoryFilter ? item.category === categoryFilter : true;
      return matchesSearch && matchesCategory;
    });
  }, [revocations, searchTerm, categoryFilter]);

  const totalPages = Math.ceil(filteredData.length / PAGE_SIZE);
  const currentData = filteredData.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  const formatList = (val: string | string[]) => {
    if (Array.isArray(val)) return val.join('、');
    return val;
  };

  return (
    <div className="p-12 max-w-6xl mx-auto">
      {/* Category Tabs */}
      <div className="flex items-center gap-12 mb-10 border-b border-white/5 pb-4">
        <TabButton 
          active={categoryFilter === null} 
          onClick={() => { setCategoryFilter(null); setCurrentPage(1); }}
          label="全部公告"
          count={revocations.length}
        />
        <TabButton 
          active={categoryFilter === 1} 
          onClick={() => { setCategoryFilter(1); setCurrentPage(1); }}
          label="第一類：賠補償"
          count={revocations.filter(r => r.category === 1).length}
        />
        <TabButton 
          active={categoryFilter === 2} 
          onClick={() => { setCategoryFilter(2); setCurrentPage(1); }}
          label="第二類：促轉會"
          count={revocations.filter(r => r.category === 2).length}
        />
      </div>

      {/* Table Container - Looking more like a Ledger */}
      <div className="bg-black/40 border border-white/5 shadow-2xl overflow-hidden backdrop-blur-sm">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-white/[0.02] border-b border-white/10">
              <th className="px-6 py-4 text-[9px] font-bold text-white/30 uppercase tracking-[0.2em]">當事人 Subject</th>
              <th className="px-6 py-4 text-[9px] font-bold text-white/30 uppercase tracking-[0.2em]">原判決案號 Case ID</th>
              <th className="px-6 py-4 text-[9px] font-bold text-white/30 uppercase tracking-[0.2em]">罪名與刑度 Crime / Sentence</th>
              <th className="px-6 py-4 text-[9px] font-bold text-white/30 uppercase tracking-[0.2em] text-right">檔案 Archive</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {currentData.map((item, idx) => (
              <tr key={idx} className="hover:bg-white/[0.02] transition-colors group">
                <td className="px-6 py-6">
                  <div className="font-bold text-white tracking-wide">{item.name}</div>
                  <div className="text-[10px] text-white/30 mt-1 font-serif italic">{formatList(item.court)}</div>
                </td>
                <td className="px-6 py-6 text-xs text-white/50 font-mono">
                  {formatList(item.case_id)}
                </td>
                <td className="px-6 py-6">
                  <div className="text-xs text-white/70 leading-snug">{formatList(item.crime)}</div>
                  <div className="text-[10px] text-archive-gold font-bold mt-1.5 uppercase tracking-wider">{formatList(item.sentence)}</div>
                </td>
                <td className="px-6 py-6 text-right">
                  {item.linked_decision_id ? (
                    <button 
                      onClick={() => onSelectDecision(item.linked_decision_id!)}
                      className="inline-flex items-center gap-2 text-archive-gold hover:text-white px-3 py-1.5 rounded transition-all border border-archive-gold/20 hover:border-archive-gold/50 text-[10px] font-bold uppercase tracking-widest"
                    >
                      調閱全文
                      <ExternalLink size={10} />
                    </button>
                  ) : (
                    <span className="text-[9px] text-white/10 uppercase font-mono tracking-tighter">No File</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {currentData.length === 0 && (
          <div className="py-32 text-center">
            <Filter size={40} className="mx-auto text-white/5 mb-4" />
            <p className="text-white/20 text-xs font-serif italic">未檢索到相關檔案記錄</p>
          </div>
        )}

        {/* Minimal Pagination */}
        <div className="px-8 py-6 bg-white/[0.02] border-t border-white/5 flex items-center justify-between">
          <div className="text-[10px] font-mono text-white/20 uppercase tracking-widest">
            Showing {((currentPage - 1) * PAGE_SIZE) + 1} - {Math.min(currentPage * PAGE_SIZE, filteredData.length)} of {filteredData.length}
          </div>
          <div className="flex items-center gap-6">
            <button 
              disabled={currentPage === 1}
              onClick={() => { setCurrentPage(p => p - 1); window.scrollTo({top: 0, behavior: 'smooth'}); }}
              className="p-2 text-white/20 hover:text-white disabled:opacity-5 transition-all"
            >
              <ChevronLeft size={20} />
            </button>
            <span className="text-xs font-bold text-archive-gold font-mono">
              {currentPage} <span className="text-white/10 mx-1">/</span> {totalPages || 1}
            </span>
            <button 
              disabled={currentPage === totalPages}
              onClick={() => { setCurrentPage(p => p + 1); window.scrollTo({top: 0, behavior: 'smooth'}); }}
              className="p-2 text-white/20 hover:text-white disabled:opacity-5 transition-all"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const TabButton = ({ active, onClick, label, count }: any) => (
  <button 
    onClick={onClick}
    className={`relative pb-4 text-xs font-bold transition-all tracking-[0.2em] uppercase ${active ? 'text-archive-gold' : 'text-white/20 hover:text-white/40'}`}
  >
    {label}
    <span className="ml-3 text-[9px] opacity-30 font-mono">[{count}]</span>
    {active && <div className="absolute bottom-0 left-0 w-full h-px bg-archive-gold" />}
  </button>
);

export default RevocationList;
