import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'RaporPejabat - Dashboard Perbandingan',
  description: 'Analisis Objektif Rekam Jejak Pejabat Publik',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="id">
      <body className="bg-slate-50 text-slate-900">{children}</body>
    </html>
  )
}
