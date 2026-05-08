"use client";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts';

interface Politician {
  name: string;
  color: string;
  scores: Record<string, number>;
}

interface RadarProps {
  p1: Politician;
  p2: Politician;
}

export default function ComparisonRadar({ p1, p2 }: RadarProps) {
  const data = [
    { subject: 'Integritas', A: p1.scores['Integritas'], B: p2.scores['Integritas'], fullMark: 10 },
    { subject: 'Janji', A: p1.scores['Janji'], B: p2.scores['Janji'], fullMark: 10 },
    { subject: 'Efisiensi', A: p1.scores['Efisiensi'], B: p2.scores['Efisiensi'], fullMark: 10 },
    { subject: 'Sosial', A: p1.scores['Sosial'], B: p2.scores['Sosial'], fullMark: 10 },
  ];

  const colors = {
    blue: '#2563eb',
    red: '#dc2626',
    indigo: '#4f46e5',
    rose: '#e11d48',
    orange: '#ea580c',
    emerald: '#059669',
    slate: '#475569',
    cyan: '#0891b2'
  };

  return (
    <div className="w-full h-[400px] bg-white p-4 rounded-xl shadow-sm border border-slate-200">
      <h3 className="text-lg font-semibold mb-4 text-center">Indeks Catatan Publik (ICP)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="subject" />
          <PolarRadiusAxis angle={30} domain={[0, 10]} />
          <Radar
            name={p1.name}
            dataKey="A"
            stroke={colors[p1.color as keyof typeof colors] || colors.slate}
            fill={colors[p1.color as keyof typeof colors] || colors.slate}
            fillOpacity={0.6}
          />
          <Radar
            name={p2.name}
            dataKey="B"
            stroke={colors[p2.color as keyof typeof colors] || colors.slate}
            fill={colors[p2.color as keyof typeof colors] || colors.slate}
            fillOpacity={0.6}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
