# 📋 Project Documentation: RaporPejabat (MVP)

**Version:** 1.0 (Final Blueprint)  
**Status:** In-Development (Phase: Backend Integration)  
**Last Updated:** 8 Mei 2026

---

## 1. Project Vision

**RaporPejabat** is an AI-based civic-tech platform aimed at enhancing public accountability in Indonesia. The platform transforms thousands of news articles into an objective **Public Record Index (ICP)**, enabling citizens to distinguish between campaign promises and ground reality without platform opinion bias.

---

## 2. Scoring Methodology: Public Record Index (ICP)

To avoid bias accusations, scoring is divided into 4 main axes:

| Axis | Description | Default Weight |
| :--- | :--- | :--- |
| **Integrity** | Legal records, LHKPN reports, BPK audits, and ethical issues. | 30% |
| **Promise Fulfillment** | Comparison between KPU Vision-Mission with news progress. | 30% |
| **Budget Efficiency** | Analysis of APBD/APBN usage (infrastructure vs luxury facilities). | 20% |
| **Social Stability** | Impact of policies on public and mass communication style. | 20% |

### **Anti-Bias Mechanism (Cross-Ownership Consensus)**
The system only assigns full weight to news confirmed by a minimum of **3 media groups with different ownership** (Example: Kompas Gramedia, Media Group, and Tempo). This mitigates hoax risks and specific media agendas.

---

## 3. Technical Architecture

### **A. Tech Stack**

*   **Frontend:** Next.js 14 (App Router), Tailwind CSS, Recharts (Radar Charts).
*   **Backend:** FastAPI (Python 3.11+), Celery + Redis (Background Processing).
*   **Database:** PostgreSQL (Metadata) + Qdrant (Vector Database for RAG).
*   **AI Engine:** GPT-4o (Chief Justice) & GPT-4o-mini (Mass Analysis).

### **B. Data Pipeline**

1.  **Ingestion:** Fetch news via NewsAPI/EventRegistry based on official keywords.
2.  **Deduplication:** Using *Locality Sensitive Hashing (LSH)* to merge similar news.
3.  **AI Analysis:** News processed through 4 Prompting stages (see section 4).
4.  **Consensus Check:** Media source verification to determine score validity.
5.  **RAG Storage:** Store facts to Vector DB so users can ask directly ("What's the progress on Rudy Mas'ud's free school promise?").

---

## 4. AI Prompts Structure (The Pipeline)

### **Stage 1: Fact Extractor & Neutralizer**

**Goal:** Extract pure facts, eliminate emotional adjectives.
```text
SYSTEM: Extract facts without opinion. Prohibited from using adjectives (great, bad, corrupt). Use factual verbs.
OUTPUT: JSON {politician_name, event_summary, key_facts, budget_mentioned}
```

### **Stage 2: Multi-Axis Scorer**

**Goal:** Assign scores from -10 to +10 on relevant axes.
```text
SYSTEM: Act as an auditor. Provide scores based on public impact. Must include 'justification' and 'evidence_citation'.
OUTPUT: JSON {axis, impact_score, justification, evidence_citation}
```

### **Stage 3: Promise Tracker**

**Goal:** Match news with Vision-Mission database (Ground Truth).
```text
SYSTEM: Match news with campaign promise list ID [X]. Determine status: FULFILLED, IN_PROGRESS, STALLED, or CONTRADICTS.
OUTPUT: JSON {promise_id, current_status, alignment_score}
```

### **Stage 4: The Chief Justice (QC)**

**Goal:** Resolve conflicts if two AI models disagree.
```text
SYSTEM: Synthesize analysis results. Provide final verdict based on hierarchy: Law > Public Welfare > Administration.
```

---

## 5. Key Features (UI/UX)

1.  **Battle Mode ⚔️:** Side-by-side comparison (Example: Rudy Mas'ud vs Dedi Mulyadi) with interactive radar charts.
2.  **Perspective Presets:** Quick buttons to change score weights (Anti-Corruption Mode vs Development Mode).
3.  **Timeline of Sentiment:** ICP fluctuation chart based on specific news events.
4.  **Evidence Explorer:** Transparent modal showing original news links behind every number.
5.  **Sentinel Status:** Visual security indicator of track record (Safe / Neutral / Warning).

---

## 6. Frontend Pages Specification

### **1. Home Page (The Landing & Search)**

This is the main entry point. The focus is ease of searching data.

- **Hero Section:** A strong message like "Monitor Promises, Demand Reality."
- **Global Search Bar:** Search for official names (Rudy Mas'ud, Dedi Mulyadi, etc).
- **Trending Battle:** A small box showing comparisons that are currently viral (e.g., "Rudy vs Dedi").
- **Stats Overview:** Number of news articles processed, number of promises tracked, and average national score.

### **2. Explorer Page (The Directory)**

A directory of all officials so users can browse.

- **Filter & Sorting:** By region (East Kalimantan, West Java, Jakarta), position (Governor, Minister), or ICP score (highest/lowest).
- **Leaderboard:** Ranking officials based on specific axes (e.g., "Most Transparent" or "Best Promise Fulfillment").

### **3. Profile Detail Page (The Deep Dive) — Most Important Page**

This is the complete "Report Card" for a single official.

- **Header:** Photo, position, and Main ICP Score.
- **Radar Chart:** Visualization of 4 axes (Integrity, Promise, Efficiency, Social).
- **AI Verdict:** A brief summary from the AI ("Chief Justice") about this official's performance.
- **Promise Tracker Tab:** List of campaign promises with their status (Fulfilled/Stalled).
- **News Timeline:** Sentiment graph over time. If the graph drops, users can click to see which news caused it.

### **4. Comparison Page (The Battle Mode)**

A dedicated page for side-by-side comparison of two officials.

- **Dual Radar Chart:** Two overlaid radar charts to see striking differences.
- **Juxtaposed Stats:** Comparison table (e.g., Rudy's Promises vs Dedi's Promises).
- **AI Comparative Summary:** AI analyzes who excels in which areas.
- **Perspective Switcher:** Button to change score weights (Anti-Corruption Mode vs Development Mode).

### **5. Methodology & Transparency Page (The Legal Shield)**

This page is critical for building trust and avoiding legal challenges.

- **Scoring Formula:** Explanation of how the numbers are generated.
- **Data Sources:** List of news outlets that are scraped.
- **Ownership Mapping:** Explanation of the media consensus system (how you handle media bias).
- **Right to Reply:** Special form for officials' staff to provide official clarification.

### **Optional Features (Pro Version)**

- **News Feed Page:** Live stream of recently analyzed news articles in real-time.
- **User Dashboard:** If login is available, users can "Follow" specific officials to receive notifications when there's new news or score changes.

### **Demo Recommendations**

Since your initial targets are Rudy Mas'ud and Dedi Mulyadi, focus on **Page 3 (Profile)** and **Page 4 (Comparison)**. These two pages will create the biggest "Wow" effect during presentations or demos.

---

## 7. Security & Legal Strategy (Safe Harbor)

1.  **Neutrality Protocol:** System instructions prohibit AI from making conclusions without news evidence.
2.  **Official Disclaimer:** Platform acts as an aggregator, not a determinant of absolute truth.
3.  **Right to Reply (Verified):** Officials can provide official clarification via institutional email (`.go.id`) which will be displayed alongside related news.
4.  **No Adjectives Policy:** Avoid defamation charges (ITE Law) by focusing on quantitative data and verified mass media quotes.

---

## 8. Roadmap & Milestones

| Phase | Duration | Key Milestone |
| :--- | :--- | :--- |
| **Phase 1: Research** | 2 Weeks | Vision-Mission Collection & Frontend Prototype Setup. |
| **Phase 2: Backend** | 4 Weeks | FastAPI Integration, Scraper Pipeline, & PostgreSQL Database. |
| **Phase 3: AI/RAG** | 3 Weeks | Qdrant Implementation, Scoring Logic, & RAG Chatbot. |
| **Phase 4: Audit** | 3 Weeks | Beta testing, third-party bias audit, & legal compliance fixes. |

---

## 9. MVP Officials List

*   **Regional:** Rudy Mas'ud, Dedi Mulyadi, Ridwan Kamil, Ganjar Pranowo, Anies Baswedan, Ahok.
*   **National:** Joko Widodo, Prabowo Subianto, Sri Mulyani Indrawati.

---

**Verified by RaporPejabat Dev Team**  
*This platform is built for Indonesian democracy transparency.* 🇮🇩
