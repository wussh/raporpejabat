# Design Spec: RaporPejabat MVP

**Date:** 2026-05-08
**Topic:** RaporPejabat MVP - The AI Auditor
**Style:** Modern FinTech (Dark Mode, Glassmorphism)

## 1. Overview
RaporPejabat is a transparency platform designed for hackathons. It uses AI to audit news articles about Indonesian public officials and dynamically update their "Kredit Skor Publik" and "Janji Kampanye" status.

## 2. Architecture
- **Framework:** Next.js 14+ (App Router, TypeScript)
- **Styling:** Tailwind CSS + Lucide Icons
- **AI Engine:** Google Gemini API (via server-side route handler)
- **Data Store:** Local `pejabat.json` file for initial state; React state for session-based updates.

## 3. Core Features
### 3.1 Live Audit Command Center
- A prominent glassmorphism input area where users paste news articles.
- Sends the news text + current official profile to Gemini API.
- Receives a structured JSON response containing score delta, reasoning, and promise updates.

### 3.2 Dynamic Credit Score
- Visualized as an animated SVG Gauge/Speedometer.
- Scores range from 0 to 1000.
- Real-time animation of score changes with "floating delta" feedback.

### 3.3 AI-Linked Promise Tracker
- Lists campaign promises from the JSON data.
- AI intelligently identifies if news impacts a specific promise status (e.g., "In Progress" -> "Completed").

### 3.4 Leaderboard
- A sleek, high-density dashboard showing "Top Trusted" and "Red Flag" officials.

## 4. Technical Details
### 4.1 System Prompt (Gemini)
```text
Kamu adalah analis politik dan auditor anti-korupsi yang sangat objektif. 
Tugasmu adalah membaca kutipan berita terkait pejabat Indonesia dan memberikan dampak terhadap "Kredit Skor Publik" mereka (Skor maksimal 1000).

Aturan Skor:
- Terbukti korupsi/tersangka: -500 poin
- Proyek mangkrak/janji palsu: -100 poin
- LHKPN tidak wajar/terlambat: -50 poin
- Menyelesaikan proyek/kebijakan transparan: +50 poin

Input Berita: "{{teks_berita}}"
Profil Pejabat: {{json_profile}}

Keluarkan HANYA format JSON yang valid:
{
  "dampak_skor": number,
  "kategori": string,
  "alasan": string,
  "promise_id_updated": string | null,
  "new_promise_status": string | null
}
```

### 4.2 Data Schema (pejabat.json)
```json
[
  {
    "id": "pjb-001",
    "nama": "Nama Pejabat",
    "jabatan": "Wali Kota X",
    "kredit_score": 750,
    "janji_kampanye": [
      { "id": "p-1", "janji": "...", "status": "..." }
    ]
  }
]
```

## 5. Success Criteria
- Instant UI feedback after "Audit" button click.
- Accurate AI parsing of news into structured score deltas.
- Visually impressive "FinTech" aesthetic that stands out in a demo.
