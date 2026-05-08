"use client";
import { useState, useEffect } from 'react';
import ComparisonRadar from '@/components/RadarChart';
import PromiseCard from '@/components/PromiseCard';
import { ShieldCheck, Newspaper } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

interface Politician {
  id: string;
  name: string;
  title: string;
  color: string;
  icp_score: number;
  sentinel_status: string;
  scores: Record<string, number>;
}

interface Promise {
  id: string;
  promise_text: string;
  category: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'STALLED' | 'CONTRADICTED';
  analysis?: string;
}

interface NewsArticle {
  id: string;
  title: string;
  source: string;
  published_at: string;
}

export default function Dashboard() {
  const [allPoliticians, setAllPoliticians] = useState<Politician[]>([]);
  const [p1Id, setP1Id] = useState<string>('rudy_masud');
  const [p2Id, setP2Id] = useState<string>('dedi_mulyadi');
  const [p1Data, setP1Data] = useState<Politician | null>(null);
  const [p2Data, setP2Data] = useState<Politician | null>(null);
  const [p1Promises, setP1Promises] = useState<Promise[]>([]);
  const [p2Promises, setP2Promises] = useState<Promise[]>([]);
  const [p1News, setP1News] = useState<NewsArticle[]>([]);
  const [p2News, setP2News] = useState<NewsArticle[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/politicians`).then(res => res.json()).then(setAllPoliticians);
  }, []);

  useEffect(() => {
    if (!p1Id) return;
    fetch(`${API_BASE}/politicians/${p1Id}`).then(res => res.json()).then(setP1Data);
    fetch(`${API_BASE}/politicians/${p1Id}/news`).then(res => res.json()).then(setP1News);
    fetch(`${API_BASE}/politicians/${p1Id}/promises`).then(res => res.json()).then(setP1Promises);
  }, [p1Id]);

  useEffect(() => {
    if (!p2Id) return;
    fetch(`${API_BASE}/politicians/${p2Id}`).then(res => res.json()).then(setP2Data);
    fetch(`${API_BASE}/politicians/${p2Id}/news`).then(res => res.json()).then(setP2News);
    fetch(`${API_BASE}/politicians/${p2Id}/promises`).then(res => res.json()).then(setP2Promises);
  }, [p2Id]);

  if (!p1Data || !p2Data) return <div className="p-8 font-bold">Memuat Data Rapor Pejabat...</div>;

  const colorVariants: any = {
    blue: 'bg-blue-600', red: 'bg-red-600', indigo: 'bg-indigo-600', rose: 'bg-rose-600', emerald: 'bg-emerald-600', slate: 'bg-slate-600', cyan: 'bg-cyan-600', orange: 'bg-orange-600'
  };

  return (
    <main className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto bg-slate-50/50">
      {/* Navigation Header */}
      <header className="mb-12 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tighter italic">RAPOR PEJABAT<span className="text-blue-600 font-normal">.AI</span></h1>
          <p className="text-slate-500 font-semibold text-sm tracking-wide mt-1 uppercase">Indeks Catatan Publik & Battle Analytics</p>
        </div>
      </header>

      {/* Battle Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <div className={`${colorVariants[p1Data.color]} rounded-3xl p-8 text-white shadow-2xl relative overflow-hidden group border-4 border-white`}>
          <div className="relative z-10">
            <div className="flex justify-between items-start mb-6">
              <span className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border border-white/30">{p1Data.title}</span>
              <select 
                value={p1Id} 
                onChange={(e) => setP1Id(e.target.value)}
                className="bg-white/10 hover:bg-white/20 border-none text-white text-xs font-bold rounded-lg px-3 py-1 focus:ring-0 cursor-pointer"
              >
                {allPoliticians.map(p => <option key={p.id} value={p.id} className="text-slate-900">{p.name}</option>)}
              </select>
            </div>
            <h2 className="text-5xl font-black tracking-tighter mb-4">{p1Data.name}</h2>
            <div className="flex gap-4">
               <div className="bg-slate-900/40 backdrop-blur-md px-4 py-2 rounded-2xl border border-white/20">
                 <p className="text-[10px] uppercase font-bold text-white/60 mb-1">Index Score</p>
                 <p className="text-2xl font-black">{p1Data.icp_score.toFixed(1)}</p>
               </div>
               <div className="bg-slate-900/40 backdrop-blur-md px-4 py-2 rounded-2xl border border-white/20">
                 <p className="text-[10px] uppercase font-bold text-white/60 mb-1">Sentinel</p>
                 <p className="text-2xl font-black">{p1Data.sentinel_status}</p>
               </div>
            </div>
          </div>
        </div>

        <div className={`${colorVariants[p2Data.color]} rounded-3xl p-8 text-white shadow-2xl relative overflow-hidden group border-4 border-white`}>
          <div className="relative z-10">
            <div className="flex justify-between items-start mb-6">
              <span className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border border-white/30">{p2Data.title}</span>
              <select 
                value={p2Id} 
                onChange={(e) => setP2Id(e.target.value)}
                className="bg-white/10 hover:bg-white/20 border-none text-white text-xs font-bold rounded-lg px-3 py-1 focus:ring-0 cursor-pointer"
              >
                {allPoliticians.map(p => <option key={p.id} value={p.id} className="text-slate-900">{p.name}</option>)}
              </select>
            </div>
            <h2 className="text-5xl font-black tracking-tighter mb-4">{p2Data.name}</h2>
            <div className="flex gap-4">
               <div className="bg-slate-900/40 backdrop-blur-md px-4 py-2 rounded-2xl border border-white/20">
                 <p className="text-[10px] uppercase font-bold text-white/60 mb-1">Index Score</p>
                 <p className="text-2xl font-black">{p2Data.icp_score.toFixed(1)}</p>
               </div>
               <div className="bg-slate-900/40 backdrop-blur-md px-4 py-2 rounded-2xl border border-white/20">
                 <p className="text-[10px] uppercase font-bold text-white/60 mb-1">Sentinel</p>
                 <p className="text-2xl font-black">{p2Data.sentinel_status}</p>
               </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
        <div className="lg:col-span-1 space-y-6">
          <ComparisonRadar p1={{name: p1Data.name, color: p1Data.color, scores: p1Data.scores}} p2={{name: p2Data.name, color: p2Data.color, scores: p2Data.scores}} />
        </div>

        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
           <div className="space-y-4">
              <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-2 flex items-center gap-2"><Newspaper size={14} /> {p1Data.name.split(' ')[0]} Latest News</h3>
              {p1News.map(n => (
                <div key={n.id} className="p-4 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-all">
                  <p className="text-xs font-bold text-slate-400 uppercase mb-1">{n.source} • {new Date(n.published_at).toLocaleDateString()}</p>
                  <p className="text-sm font-semibold text-slate-800">{n.title}</p>
                </div>
              ))}
              <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 pt-4 mb-2">{p1Data.name.split(' ')[0]} Promise Tracker</h3>
              {p1Promises.slice(0, 4).map(promise => (
                <PromiseCard
                  key={promise.id}
                  id={promise.id}
                  promise={promise.promise_text}
                  category={promise.category}
                  status={promise.status}
                  analysis={promise.analysis}
                />
              ))}
           </div>
           <div className="space-y-4">
              <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-2 flex items-center gap-2"><Newspaper size={14} /> {p2Data.name.split(' ')[0]} Latest News</h3>
              {p2News.map(n => (
                <div key={n.id} className="p-4 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-all">
                  <p className="text-xs font-bold text-slate-400 uppercase mb-1">{n.source} • {new Date(n.published_at).toLocaleDateString()}</p>
                  <p className="text-sm font-semibold text-slate-800">{n.title}</p>
                </div>
              ))}
              <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 pt-4 mb-2">{p2Data.name.split(' ')[0]} Promise Tracker</h3>
              {p2Promises.slice(0, 4).map(promise => (
                <PromiseCard
                  key={promise.id}
                  id={promise.id}
                  promise={promise.promise_text}
                  category={promise.category}
                  status={promise.status}
                  analysis={promise.analysis}
                />
              ))}
           </div>
        </div>

        <div className="lg:col-span-1">
          <div className="bg-amber-600 rounded-3xl p-6 text-white shadow-xl relative overflow-hidden">
            <ShieldCheck className="absolute -bottom-4 -right-4 opacity-10" size={100} />
            <h4 className="text-xs font-black uppercase tracking-widest mb-4 opacity-80 flex items-center gap-2">
              Chief Justice AI Verdict
            </h4>
            <p className="text-sm font-bold leading-relaxed">
              Sistem telah mendeteksi {p1News.length + p2News.length} berita terbaru yang mempengaruhi ICP.
              <br/><br/>
              **{p1Data.name}** saat ini memiliki rekam jejak yang {p1Data.sentinel_status === 'Warning' ? 'perlu diawasi ketat' : 'stabil'}.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
