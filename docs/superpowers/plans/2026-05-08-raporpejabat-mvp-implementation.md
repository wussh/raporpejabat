# RaporPejabat MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a functional MVP for "RaporPejabat" using Next.js and Gemini API to audit Indonesian officials' news and update their credit scores.

**Architecture:** Next.js App Router with a local JSON "ledger" (`pejabat.json`). AI audits are handled via a server-side API route that communicates with Google Gemini. State is managed locally in React for real-time UI updates during the session.

**Tech Stack:** Next.js 14+, TypeScript, Tailwind CSS, Lucide Icons, Google Generative AI SDK.

---

### Task 1: Project Scaffolding

**Files:**
- Create: `package.json`, `tsconfig.json`, `next.config.mjs`, `tailwind.config.ts`, `postcss.config.mjs`
- Create: `app/layout.tsx`, `app/page.tsx`, `app/globals.css`

- [ ] **Step 1: Initialize Next.js with Tailwind**

Run: `npx create-next-app@latest . --ts --tailwind --eslint --app --src-dir false --import-alias "@/*" --use-npm --no-git`
Expected: Project structure created in root.

- [ ] **Step 2: Add Lucide Icons and Google AI SDK**

Run: `npm install lucide-react @google/generative-ai clsx tailwind-merge`
Expected: Dependencies installed.

- [ ] **Step 3: Verify basic dev server**

Run: `npm run dev` in background, then `curl http://localhost:3000`
Expected: Next.js default page or a 200 OK.

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "chore: initial scaffold"
```

---

### Task 2: Data Schema & Seed Data

**Files:**
- Create: `types/index.ts`
- Create: `data/pejabat.json`

- [ ] **Step 1: Define TypeScript Types**

Create `types/index.ts`:
```typescript
export interface PromiseItem {
  id: string;
  janji: string;
  status: 'Not Started' | 'In Progress' | 'Stalled' | 'Completed';
}

export interface Pejabat {
  id: string;
  nama: string;
  jabatan: string;
  partai?: string;
  kredit_score: number;
  status_lhkpn: string;
  janji_kampanye: PromiseItem[];
  red_flags: string[];
}

export interface AuditResponse {
  dampak_skor: number;
  kategori: string;
  alasan: string;
  promise_id_updated: string | null;
  new_promise_status: PromiseItem['status'] | null;
}
```

- [ ] **Step 2: Create Seed JSON**

Create `data/pejabat.json`:
```json
[
  {
    "id": "pjb-001",
    "nama": "Budi Santoso",
    "jabatan": "Wali Kota X",
    "partai": "Partai Maju",
    "kredit_score": 750,
    "status_lhkpn": "Tepat Waktu",
    "janji_kampanye": [
      { "id": "p1", "janji": "Membangun 10 Taman Kota", "status": "In Progress" },
      { "id": "p2", "janji": "Subsidi Transportasi Publik", "status": "Completed" }
    ],
    "red_flags": []
  },
  {
    "id": "pjb-002",
    "nama": "Tono Wijaya",
    "jabatan": "Bupati Y",
    "partai": "Partai Sejahtera",
    "kredit_score": 320,
    "status_lhkpn": "Terlambat",
    "janji_kampanye": [
      { "id": "p3", "janji": "Pembangunan RSUD Baru", "status": "Stalled" }
    ],
    "red_flags": ["Diperiksa KPK terkait dana bansos 2024"]
  }
]
```

- [ ] **Step 3: Commit**

```bash
git add types/index.ts data/pejabat.json
git commit -m "feat: add data schema and seed data"
```

---

### Task 3: Dashboard & Leaderboard UI

**Files:**
- Modify: `app/page.tsx`
- Create: `components/Leaderboard.tsx`
- Create: `components/PejabatCard.tsx`

- [ ] **Step 1: Create PejabatCard component**

Create `components/PejabatCard.tsx`:
```tsx
import { Pejabat } from '@/types';
import { TrendingUp, TrendingDown, User } from 'lucide-react';
import Link from 'next/link';

export default function PejabatCard({ pejabat }: { pejabat: Pejabat }) {
  const isPositive = pejabat.kredit_score > 500;
  return (
    <Link href={`/pejabat/${pejabat.id}`} className="block group">
      <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 p-4 rounded-xl hover:border-indigo-500/50 transition-all duration-300">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center">
              <User className="text-slate-400" size={20} />
            </div>
            <div>
              <h3 className="font-semibold text-white group-hover:text-indigo-400 transition-colors">{pejabat.nama}</h3>
              <p className="text-xs text-slate-400">{pejabat.jabatan}</p>
            </div>
          </div>
          <div className={`flex items-center gap-1 font-mono font-bold ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {pejabat.kredit_score}
            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          </div>
        </div>
      </div>
    </Link>
  );
}
```

- [ ] **Step 2: Create Leaderboard and Main Page**

Modify `app/page.tsx`:
```tsx
import data from '@/data/pejabat.json';
import PejabatCard from '@/components/PejabatCard';
import { Pejabat } from '@/types';

export default function Home() {
  const pejabatList = data as Pejabat[];
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            RaporPejabat
          </h1>
          <p className="text-slate-400 mt-2">Transparansi Rekam Jejak Tanpa Bias.</p>
        </header>

        <section className="mb-12">
          <h2 className="text-xl font-semibold mb-6">Leaderboard Publik</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pejabatList.map((p) => (
              <PejabatCard key={p.id} pejabat={p} />
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add app/page.tsx components/PejabatCard.tsx
git commit -m "feat: implement dashboard and leaderboard UI"
```

---

### Task 4: Official Detail Page & Score Gauge

**Files:**
- Create: `app/pejabat/[id]/page.tsx`
- Create: `components/ScoreGauge.tsx`
- Create: `components/PromiseTracker.tsx`

- [ ] **Step 1: Create ScoreGauge Component**

Create `components/ScoreGauge.tsx`:
```tsx
export default function ScoreGauge({ score }: { score: number }) {
  const percentage = (score / 1000) * 100;
  const rotation = (percentage / 100) * 180 - 90;

  return (
    <div className="relative w-64 h-32 overflow-hidden mx-auto">
      <div className="absolute inset-0 border-[12px] border-slate-800 rounded-t-full"></div>
      <div 
        className="absolute inset-0 border-[12px] border-indigo-500 rounded-t-full transition-all duration-1000 ease-out"
        style={{ clipPath: `inset(0 ${100 - (percentage/2 + 50)}% 0 0)`, transformOrigin: 'bottom center' }}
      ></div>
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
        <span className="text-4xl font-black text-white">{score}</span>
        <p className="text-xs text-slate-500 uppercase tracking-widest">Credit Score</p>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Implement Detail Page**

Create `app/pejabat/[id]/page.tsx` (simplified initial version):
```tsx
import data from '@/data/pejabat.json';
import { Pejabat } from '@/types';
import ScoreGauge from '@/components/ScoreGauge';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function PejabatDetail({ params }: { params: { id: string } }) {
  const pejabat = (data as Pejabat[]).find(p => p.id === params.id);
  if (!pejabat) return <div>Not Found</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <Link href="/" className="flex items-center gap-2 text-slate-400 hover:text-white mb-8">
        <ArrowLeft size={20} /> Kembali
      </Link>
      <div className="max-w-4xl mx-auto bg-slate-900/40 rounded-3xl p-8 border border-slate-800">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold">{pejabat.nama}</h1>
          <p className="text-slate-400">{pejabat.jabatan} • {pejabat.partai}</p>
        </div>
        <ScoreGauge score={pejabat.kredit_score} />
        {/* Audit Center and Promises will go here */}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add app/pejabat/[id]/page.tsx components/ScoreGauge.tsx
git commit -m "feat: implement detail page and score gauge"
```

---

### Task 5: Gemini API Integration

**Files:**
- Create: `app/api/audit/route.ts`
- Create: `.env.local`

- [ ] **Step 1: Set up Environment Variables**

Create `.env.local`:
```text
GEMINI_API_KEY=YOUR_API_KEY_HERE
```
Note: Remind user to fill this in.

- [ ] **Step 2: Implement API Route**

Create `app/api/audit/route.ts`:
```typescript
import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const { news, profile } = await req.json();
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

  const prompt = `
    Kamu adalah analis politik dan auditor anti-korupsi yang sangat objektif. 
    Tugasmu adalah membaca kutipan berita terkait pejabat Indonesia dan memberikan dampak terhadap "Kredit Skor Publik" mereka (Skor maksimal 1000).

    Aturan Skor:
    - Terbukti korupsi/tersangka: -500 poin
    - Proyek mangkrak/janji palsu: -100 poin
    - LHKPN tidak wajar/terlambat: -50 poin
    - Menyelesaikan proyek/kebijakan transparan: +50 poin

    Input Berita: "${news}"
    Profil Pejabat Saat Ini: ${JSON.stringify(profile)}

    Keluarkan HANYA format JSON yang valid tanpa markdown:
    {
      "dampak_skor": number,
      "kategori": string,
      "alasan": string,
      "promise_id_updated": string | null,
      "new_promise_status": string | null
    }
  `;

  const result = await model.generateContent(prompt);
  const response = await result.response;
  const text = response.text();
  
  try {
    const json = JSON.parse(text);
    return NextResponse.json(json);
  } catch (e) {
    return NextResponse.json({ error: "Failed to parse AI response" }, { status: 500 });
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add app/api/audit/route.ts .env.local
git commit -m "feat: add gemini api audit route"
```

---

### Task 6: Audit Center UI & State Logic

**Files:**
- Create: `components/AuditCenter.tsx`
- Modify: `app/pejabat/[id]/page.tsx`

- [ ] **Step 1: Create AuditCenter Component**

Create `components/AuditCenter.tsx`:
```tsx
'use client';
import { useState } from 'react';
import { Pejabat, AuditResponse } from '@/types';
import { Search, Loader2 } from 'lucide-react';

export default function AuditCenter({ pejabat, onAuditComplete }: { pejabat: Pejabat, onAuditComplete: (res: AuditResponse) => void }) {
  const [news, setNews] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAudit = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ news, profile: pejabat }),
      });
      const data = await res.json();
      onAuditComplete(data);
      setNews('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-12 p-6 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl backdrop-blur-md">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Search size={18} /> Audit Berita Live
      </h3>
      <textarea 
        className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
        rows={4}
        placeholder="Tempel berita terbaru di sini untuk mulai audit..."
        value={news}
        onChange={(e) => setNews(e.target.value)}
      />
      <button 
        onClick={handleAudit}
        disabled={loading || !news}
        className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all"
      >
        {loading ? <Loader2 className="animate-spin" size={20} /> : 'Mulai Audit'}
      </button>
    </div>
  );
}
```

- [ ] **Step 2: Integrate Audit logic into Detail Page**

Modify `app/pejabat/[id]/page.tsx` to handle state (Convert to client component for MVP simplicity in tracking changes):
```tsx
'use client';
import { useState } from 'react';
import staticData from '@/data/pejabat.json';
import { Pejabat, AuditResponse } from '@/types';
import ScoreGauge from '@/components/ScoreGauge';
import AuditCenter from '@/components/AuditCenter';
import { ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function PejabatDetail({ params }: { params: { id: string } }) {
  const initialPejabat = (staticData as Pejabat[]).find(p => p.id === params.id);
  const [pejabat, setPejabat] = useState<Pejabat | null>(initialPejabat || null);
  const [lastResult, setLastResult] = useState<AuditResponse | null>(null);

  if (!pejabat) return <div className="p-8">Pejabat tidak ditemukan.</div>;

  const handleAuditComplete = (res: AuditResponse) => {
    setLastResult(res);
    setPejabat(prev => {
      if (!prev) return null;
      const updatedPromises = prev.janji_kampanye.map(p => {
        if (p.id === res.promise_id_updated) {
          return { ...p, status: res.new_promise_status || p.status };
        }
        return p;
      });
      return {
        ...prev,
        kredit_score: Math.max(0, Math.min(1000, prev.kredit_score + res.dampak_skor)),
        janji_kampanye: updatedPromises
      };
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-4 md:p-8">
      <Link href="/" className="flex items-center gap-2 text-slate-400 hover:text-white mb-8">
        <ArrowLeft size={20} /> Kembali ke Leaderboard
      </Link>
      
      <div className="max-w-4xl mx-auto">
        <div className="bg-slate-900/40 rounded-3xl p-6 md:p-12 border border-slate-800">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-black mb-2">{pejabat.nama}</h1>
            <p className="text-indigo-400 font-medium uppercase tracking-widest text-sm">{pejabat.jabatan}</p>
          </div>

          <ScoreGauge score={pejabat.kredit_score} />

          {lastResult && (
            <div className={`mt-8 p-4 rounded-xl border flex gap-3 ${lastResult.dampak_skor >= 0 ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-rose-500/10 border-rose-500/30 text-rose-400'}`}>
              {lastResult.dampak_skor >= 0 ? <CheckCircle2 /> : <AlertCircle />}
              <div>
                <p className="font-bold">Audit Selesai: {lastResult.dampak_skor > 0 ? '+' : ''}{lastResult.dampak_skor} Poin</p>
                <p className="text-sm opacity-80">{lastResult.alasan}</p>
              </div>
            </div>
          )}

          <AuditCenter pejabat={pejabat} onAuditComplete={handleAuditComplete} />

          <div className="mt-12">
            <h3 className="text-xl font-bold mb-6">Janji Kampanye</h3>
            <div className="space-y-4">
              {pejabat.janji_kampanye.map(p => (
                <div key={p.id} className="bg-slate-950/50 border border-slate-800 p-4 rounded-xl flex justify-between items-center">
                  <span className="text-slate-300">{p.janji}</span>
                  <span className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-tighter ${
                    p.status === 'Completed' ? 'bg-emerald-500/20 text-emerald-400' :
                    p.status === 'In Progress' ? 'bg-indigo-500/20 text-indigo-400' :
                    'bg-slate-800 text-slate-400'
                  }`}>
                    {p.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add components/AuditCenter.tsx app/pejabat/[id]/page.tsx
git commit -m "feat: implement audit center and real-time state updates"
```

---

### Task 7: Polishing & Visual Effects

- [ ] **Step 1: Add Global Fonts and Styles**

Modify `app/globals.css` to include a nice dark gradient background:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 255, 255, 255;
  --background-start-rgb: 2, 6, 23;
  --background-end-rgb: 0, 0, 0;
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}
```

- [ ] **Step 2: Final Demo check**

Run the app, paste a fake news like "Budi Santoso tertangkap tangan menerima suap 5 miliar" and verify the score drops and an alert appears.

- [ ] **Step 3: Commit**

```bash
git add app/globals.css
git commit -m "style: final UI polish and global styles"
```
