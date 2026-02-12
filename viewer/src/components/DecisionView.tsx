import React, { useState, useEffect, useMemo } from 'react';
import type { Decision, StructuredReasoning } from '../types';
import { Calendar, User, Bookmark, Loader2, Scale, ShieldAlert, Stamp } from 'lucide-react';
import { analyzeText } from '../utils/analysis';

interface DecisionViewProps {
  id: string | null;
  searchQuery?: string;
}

const DecisionView: React.FC<DecisionViewProps> = ({ id, searchQuery = '' }) => {
  const [data, setData] = useState<Decision | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const filename = id.replace(/_json$/, '.json');
        const response = await fetch(`/decisions/${filename}`);
        if (!response.ok) throw new Error('無法載入檔案');
        const json = await response.json();
        setData(json);
      } catch (err: any) { setError(err.message); } finally { setLoading(false); }
    };
    fetchData();
  }, [id]);

  const analysis = useMemo(() => {
    if (!data) return { crimes: [], reasons: [], sentences: [] };
    const fullText = (data.content.full_text || '') + (data.content.main_text || '') + (data.content.reasoning || '');
    return analyzeText(fullText);
  }, [data]);

  const highlightText = (text: string) => {
    if (!searchQuery.trim() || !text) return text;
    const parts = text.split(new RegExp(`(${searchQuery})`, 'gi'));
    return (
      <>
        {parts.map((part, i) => 
          part.toLowerCase() === searchQuery.toLowerCase() 
            ? <mark key={i} className="bg-red-900/10 text-archive-red border-b border-archive-red px-0.5">{part}</mark> 
            : part
        )}
      </>
    );
  };

  if (!id) {
    return (
      <div className="h-full flex flex-col items-center justify-center opacity-20 grayscale">
        <Scale size={100} strokeWidth={1} />
        <p className="mt-4 font-serif tracking-widest uppercase text-xs">Awaiting Document Selection</p>
      </div>
    );
  }

  if (loading) return <div className="h-full flex items-center justify-center"><Loader2 className="animate-spin opacity-20" /></div>;
  if (error || !data) return <div className="p-20 text-red-900 font-serif">檔案調閱失敗: {error}</div>;

  return (
    <div className="min-h-full py-20 px-4 md:px-12 flex justify-center">
      <div className="document-dossier w-full max-w-4xl p-12 md:p-20 relative overflow-hidden">
        
        {/* Dossier Header - Old School */}
        <header className="border-b-2 border-black/80 pb-12 mb-16 relative">
          <div className="flex justify-between items-start mb-12">
            <div className="font-mono text-[10px] leading-tight opacity-60">
              NATIONAL ARCHIVES ADMINISTRATION<br/>
              TRANSITIONAL JUSTICE COMMISSION<br/>
              CLASSIFIED: DECLASSIFIED
            </div>
            <div className="text-right">
              <div className="border border-black px-4 py-1 text-xs font-bold uppercase tracking-tighter">
                案序 {id ? id.split('_')[0].replace('促轉司字第', '') : '---'}
              </div>
            </div>
          </div>

          <h1 className="text-4xl font-bold text-black mb-10 font-serif text-center tracking-tighter">
            促 進 轉 型 正 義 委 員 會 決 定 書
          </h1>

          <div className="flex flex-wrap justify-center gap-x-12 gap-y-4 text-sm font-serif italic text-black/70">
            <div className="flex items-center gap-2">
              <span className="not-italic text-[10px] font-sans font-bold uppercase tracking-widest opacity-40">Case No.</span>
              {data.metadata.case_no}
            </div>
            <div className="flex items-center gap-2">
              <span className="not-italic text-[10px] font-sans font-bold uppercase tracking-widest opacity-40">Subject</span>
              <span className="font-bold underline decoration-double">{data.metadata.subject}</span>
            </div>
          </div>
        </header>

        {/* The "Historical Tags" - Looking more like folder tabs */}
        <div className="flex flex-wrap gap-4 mb-16 border-b border-black/10 pb-10">
          <TagSection label="涉嫌罪名" items={analysis.crimes} color="text-red-900" />
          <TagSection label="平復理由" items={analysis.reasons} color="text-emerald-900" />
          <TagSection label="原始刑度" items={analysis.sentences} color="text-purple-900" />
        </div>

        {/* Content Section */}
        <div className="space-y-24 relative">
          
          {/* Verdict - The "Finality" */}
          <section className="relative">
             <div className="mb-6 flex items-center gap-4">
                <ShieldAlert size={16} className="text-archive-red" />
                <h2 className="font-bold text-xs uppercase tracking-[0.3em] text-black">決定主文 Verdict</h2>
             </div>
             
             <div className="relative border-y-4 border-black/80 py-12 px-2 my-8 bg-black/[0.02]">
                {/* The "Considered Revoked" Stamp - Vivid & Raw */}
                <div className="absolute right-0 top-1/2 -translate-y-1/2 opacity-30 rotate-[-10deg] pointer-events-none select-none mix-blend-multiply border-[6px] border-archive-red p-4 rounded-xl flex flex-col items-center">
                    <div className="text-archive-red font-black text-6xl font-serif tracking-tighter">視為撤銷</div>
                    <div className="text-archive-red text-[10px] font-bold uppercase tracking-widest border-t-2 border-archive-red mt-2 pt-1">Judicial Injustice Remedied</div>
                </div>

                <div className="text-3xl font-serif leading-relaxed text-black text-justify relative z-10 antialiased font-semibold">
                  {highlightText(data.content.main_text || '')}
                </div>
             </div>
          </section>

          {/* Facts & Reasoning - Like a Typed Document */}
          <div className="grid grid-cols-1 gap-20">
            {data.content.facts && (
              <section className="pl-10 border-l border-black/10">
                <h2 className="font-bold text-[10px] uppercase tracking-[0.3em] text-black/40 mb-6">事實背景 Facts</h2>
                <div className="text-lg font-serif leading-[2] text-black/80 text-justify whitespace-pre-wrap">
                  {highlightText(data.content.facts)}
                </div>
              </section>
            )}

            <section className="pl-10 border-l border-black/10">
              <h2 className="font-bold text-[10px] uppercase tracking-[0.3em] text-black/40 mb-10">判決理由 Reasoning</h2>
              <div className="space-y-16">
                {data.structured_reasoning && data.structured_reasoning.length > 0 ? (
                  data.structured_reasoning.map((item, idx) => (
                    <ReasoningBlock key={idx} node={item} highlight={highlightText} />
                  ))
                ) : (
                  <div className="text-lg font-serif leading-[2] text-black/80 text-justify whitespace-pre-wrap">
                    {highlightText(data.content.reasoning || '')}
                  </div>
                )}
              </div>
            </section>
          </div>
        </div>

        <footer className="mt-32 pt-16 border-t-2 border-black/80 flex justify-between items-end">
          <div className="font-mono text-[9px] opacity-40">
            OFFICIAL TRANSCRIPT<br/>
            NOT FOR REPRODUCTION WITHOUT AUTHORIZATION
          </div>
          <div className="text-right">
             <div className="font-serif italic text-sm mb-2">{data.metadata.date || '中華民國 --- 年 -- 月 -- 日'}</div>
             <div className="font-bold text-lg tracking-widest uppercase">促進轉型正義委員會</div>
          </div>
        </footer>
      </div>
    </div>
  );
};

const TagSection = ({ label, items, color }: { label: string, items: string[], color: string }) => {
  if (!items.length) return null;
  return (
    <div className="flex gap-3 items-center bg-black/[0.03] px-4 py-2 rounded border border-black/5">
      <span className="text-[10px] font-bold text-black/30 uppercase tracking-tighter whitespace-nowrap">{label}</span>
      <div className="flex gap-x-4 gap-y-1 flex-wrap">
        {items.map(it => <span key={it} className={`text-sm font-serif font-bold ${color}`}>{it}</span>)}
      </div>
    </div>
  );
};

const ReasoningBlock: React.FC<{ 
  node: StructuredReasoning, 
  highlight: (t: string) => React.ReactNode 
}> = ({ node, highlight }) => {
  return (
    <div className="mb-12">
      <h3 className="text-lg font-bold text-black mb-6 font-serif underline decoration-black/10 underline-offset-8">
        {node.text}
      </h3>
      <div className="space-y-8">
        {node.content.map((p, i) => (
          <p key={i} className="text-lg font-serif leading-[2] text-black/80 text-justify">
            {highlight(p)}
          </p>
        ))}
      </div>
      {node.children && node.children.length > 0 && (
        <div className="mt-12 pl-12 border-l-2 border-black/5 space-y-16">
          {node.children.map((child, i) => (
            <ReasoningBlock key={i} node={child} highlight={highlight} />
          ))}
        </div>
      )}
    </div>
  );
};

export default DecisionView;
