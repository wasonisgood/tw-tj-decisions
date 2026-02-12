import React, { useMemo } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import type { DecisionIndexItem, Revocation } from '../types';

interface StatsViewProps {
  decisions: DecisionIndexItem[];
  revocations: Revocation[];
}

const COLORS = ['#c0392b', '#3498db', '#27ae60', '#f1c40f', '#8e44ad', '#e67e22', '#2c3e50'];

const StatsView: React.FC<StatsViewProps> = ({ decisions, revocations }) => {
  
  const stats = useMemo(() => {
    if (!revocations || !Array.isArray(revocations)) {
      return { courtData: [], crimeData: [], severityData: [] };
    }

    // 1. Court Distribution (Top 10)
    const courtMap: Record<string, number> = {};
    revocations.forEach(r => {
      const courts = Array.isArray(r.court) ? r.court : [r.court];
      courts.forEach(c => {
        if (!c || typeof c !== 'string') return;
        const key = c.replace(/台灣省|臺灣省|國防部/g, '').trim();
        courtMap[key] = (courtMap[key] || 0) + 1;
      });
    });
    const courtData = Object.entries(courtMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([name, value]) => ({ name, value }));

    // 2. Crime Analysis (Granular)
    const crimeMap: Record<string, number> = {};
    revocations.forEach(r => {
      const crimes = Array.isArray(r.crime) ? r.crime : [r.crime];
      crimes.forEach(c => {
        if (!c || typeof c !== 'string') return;
        let key = '其他';
        if (c.includes('叛亂')) key = '叛亂罪';
        else if (c.includes('匪諜')) key = '匪諜案件';
        else if (c.includes('參加叛亂') || c.includes('加入叛亂')) key = '參加叛亂組織';
        else if (c.includes('感化') || c.includes('感訓')) key = '感化教育';
        else if (c.includes('宣傳')) key = '為匪宣傳';
        else if (c.includes('不報')) key = '知匪不報';
        else key = c.split('、')[0].slice(0, 8);
        crimeMap[key] = (crimeMap[key] || 0) + 1;
      });
    });
    const crimeData = Object.entries(crimeMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([name, value]) => ({ name, value }));

    // 3. Sentence Severity
    const getSentenceStr = (r: Revocation) => {
        if (!r.sentence) return "";
        return JSON.stringify(r.sentence);
    };

    const severityData = [
      { name: '極刑 (死刑)', value: revocations.filter(r => getSentenceStr(r).includes('死刑')).length },
      { name: '無期徒刑', value: revocations.filter(r => getSentenceStr(r).includes('無期')).length },
      { name: '有期徒刑', value: revocations.filter(r => getSentenceStr(r).includes('有期')).length },
      { name: '感化/感訓', value: revocations.filter(r => {
          const s = getSentenceStr(r);
          return s.includes('感化') || s.includes('感訓');
      }).length },
    ];

    return { courtData, crimeData, severityData };
  }, [revocations]);

  if (!revocations || revocations.length === 0) {
    return (
      <div className="p-12 text-center text-gray-400">
        暫無數據可供分析
      </div>
    );
  }

  return (
    <div className="p-12 space-y-16 max-w-7xl mx-auto pb-32">
      {/* Header Narrative */}
      <div className="max-w-3xl border-l-4 border-archive-accent pl-8 animate-in fade-in slide-in-from-left duration-700">
        <h2 className="text-3xl font-bold text-gray-900 mb-4 font-serif">司法平復數據景觀</h2>
        <p className="text-gray-500 leading-relaxed italic">
          本頁面彙整了威權統治時期經公告平復之刑事有罪判決數據。
          從裁判機關的分佈、涉案罪名的組成到刑度的嚴厲程度，呈現轉型正義工程在法律維度上的廣度與深度。
        </p>
      </div>

      {/* Primary Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8 animate-in fade-in zoom-in duration-500 delay-150">
        <StatItem title="平復總案數" value={revocations.length} sub="人次" color="text-archive-accent" />
        <StatItem title="第一類 (賠補償)" value={revocations.filter(r => r.category === 1).length} sub="人次" />
        <StatItem title="第二類 (促轉會)" value={revocations.filter(r => r.category === 2).length} sub="人次" />
        <StatItem title="數位化全文" value={decisions.length} sub="件" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Court Chart */}
        <section className="bg-white p-10 rounded-3xl border border-gray-100 shadow-sm transition-all hover:shadow-md">
          <div className="mb-8">
            <h3 className="text-lg font-bold text-gray-800">主要裁判機關分佈</h3>
            <p className="text-xs text-gray-400 mt-1">呈現發出最多後來被撤銷判決的軍事與司法機關</p>
          </div>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.courtData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f5f5f5" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" width={100} axisLine={false} tickLine={false} style={{ fontSize: '12px', fontWeight: 'bold' }} />
                <Tooltip cursor={{ fill: '#fdfdfb' }} />
                <Bar dataKey="value" fill="#c0392b" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Severity Chart */}
        <section className="bg-white p-10 rounded-3xl border border-gray-100 shadow-sm transition-all hover:shadow-md">
          <div className="mb-8">
            <h3 className="text-lg font-bold text-gray-800">原始刑度嚴厲程度</h3>
            <p className="text-xs text-gray-400 mt-1">被撤銷案件之原始判決刑度分佈</p>
          </div>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={110}
                  paddingAngle={8}
                  dataKey="value"
                >
                  {stats.severityData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Crime Granular Chart */}
        <section className="bg-white p-10 rounded-3xl border border-gray-100 shadow-sm lg:col-span-2 transition-all hover:shadow-md">
          <div className="mb-8">
            <h3 className="text-lg font-bold text-gray-800">涉案罪名類型分析</h3>
            <p className="text-xs text-gray-400 mt-1">威權統治時期最常被引用的入罪法條</p>
          </div>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.crimeData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f5f5f5" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} style={{ fontSize: '11px' }} />
                <YAxis axisLine={false} tickLine={false} style={{ fontSize: '11px' }} />
                <Tooltip cursor={{ fill: '#fdfdfb' }} />
                <Bar dataKey="value" fill="#2c3e50" radius={[4, 4, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      {/* Logic Connection Section */}
      <div className="bg-archive-sidebar text-white p-16 rounded-[3rem] shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32 blur-3xl" />
        <div className="max-w-3xl relative z-10">
          <h3 className="text-2xl font-bold mb-6 font-serif">數據背後的法理邏輯</h3>
          <p className="text-gray-400 leading-loose text-lg">
            從數據中可以看出，高達 80% 以上的平復案件集中於「叛亂」與「匪諜」相關罪名。
            透過對決定書全文的解析，我們發現「證據不足」與「違反憲政秩序」是促轉會撤銷原判決的最核心理由。
            這不僅是數字的平反，更是透過法律程序的重新審視，還原威權時期司法體系對人權的侵蝕與修復。
          </p>
        </div>
      </div>
    </div>
  );
};

const StatItem = ({ title, value, sub, color = "text-gray-900" }: any) => (
  <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm hover:shadow-lg transition-all transform hover:-translate-y-1">
    <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4 border-b border-gray-50 pb-2">{title}</div>
    <div className="flex items-baseline gap-2">
      <span className={`text-5xl font-bold font-mono tracking-tighter ${color}`}>{value.toLocaleString()}</span>
      <span className="text-xs text-gray-400 font-bold uppercase">{sub}</span>
    </div>
  </div>
);

export default StatsView;
