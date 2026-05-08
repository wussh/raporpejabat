# 📋 Dokumentasi Proyek: RaporPejabat (MVP)

**Versi:** 1.0 (Final Blueprint)  
**Status:** Dalam Pengembangan (Fase: Integrasi Backend)  
**Terakhir Diperbarui:** 8 Mei 2026

---

## 1. Visi Proyek

**RaporPejabat** adalah platform *civic-tech* berbasis AI yang bertujuan meningkatkan akuntabilitas publik di Indonesia. Platform ini mengubah ribuan data berita menjadi **Indeks Catatan Publik (ICP)** yang objektif, memungkinkan masyarakat membedakan antara janji kampanye dan realitas lapangan tanpa bias opini platform.

---

## 2. Metodologi Skoring: Indeks Catatan Publik (ICP)

Untuk menghindari tuduhan bias, skoring dibagi menjadi 4 sumbu (*axes*) utama:

| Sumbu | Deskripsi | Bobot Default |
| :--- | :--- | :--- |
| **Integritas** | Catatan hukum, laporan LHKPN, audit BPK, dan isu etika. | 30% |
| **Realisasi Janji** | Komparasi antara Visi-Misi KPU dengan progres di berita. | 30% |
| **Efisiensi Anggaran** | Analisis penggunaan APBD/APBN (infrastruktur vs fasilitas mewah). | 20% |
| **Stabilitas Sosial** | Dampak kebijakan terhadap publik dan gaya komunikasi massa. | 20% |

### **Mekanisme Anti-Bias (Cross-Ownership Consensus)**

Sistem hanya memberikan bobot penuh pada berita yang dikonfirmasi oleh minimal **3 grup media yang berbeda pemiliknya** (Contoh: Kompas Gramedia, Media Group, dan Tempo). Hal ini memitigasi risiko hoaks atau agenda media tertentu.

---

## 3. Arsitektur Teknis

### **A. Tech Stack**

*   **Frontend:** Next.js 14 (App Router), Tailwind CSS, Recharts (Radar Charts).
*   **Backend:** FastAPI (Python 3.11+), Celery + Redis (Background Processing).
*   **Database:** PostgreSQL (Metadata) + Qdrant (Vector Database untuk RAG).
*   **AI Engine:** GPT-4o (Chief Justice) & GPT-4o-mini (Mass Analysis).

### **B. Data Pipeline**

1.  **Ingestion:** Mengambil berita via NewsAPI/EventRegistry berdasarkan keyword tokoh.
2.  **Deduplication:** Menggunakan *Locality Sensitive Hashing (LSH)* untuk menggabungkan berita serupa.
3.  **AI Analysis:** Berita diproses melalui 4 tahap Prompting (lihat bagian 4).
4.  **Consensus Check:** Verifikasi sumber media untuk menentukan validitas skor.
5.  **RAG Storage:** Menyimpan fakta ke Vector DB agar user bisa bertanya langsung ("Apa progres janji sekolah gratis Rudy Mas'ud?").

---

## 4. Struktur AI Prompts (The Pipeline)

### **Tahap 1: Fact Extractor & Neutralizer**

**Goal:** Ekstraksi fakta murni, buang kata sifat emosional.
```text
SYSTEM: Ekstrak fakta tanpa opini. Dilarang menggunakan kata sifat (hebat, buruk, korup). Gunakan kata kerja faktual.
OUTPUT: JSON {politician_name, event_summary, key_facts, budget_mentioned}
```

### **Tahap 2: Multi-Axis Scorer**

**Goal:** Memberikan skor -10 hingga +10 pada axis yang relevan.
```text
SYSTEM: Bertindak sebagai auditor. Berikan skor berdasarkan dampak publik. Wajib sertakan 'justification' dan 'evidence_citation'.
OUTPUT: JSON {axis, impact_score, justification, evidence_citation}
```

### **Tahap 3: Promise Tracker**

**Goal:** Mencocokkan berita dengan database Visi-Misi (Ground Truth).
```text
SYSTEM: Cocokkan berita dengan daftar janji kampanye ID [X]. Tentukan status: TERWUJUD, PROGRES, MANGKRAK, atau BERTENTANGAN.
OUTPUT: JSON {promise_id, current_status, alignment_score}
```

### **Tahap 4: The Chief Justice (QC)**

**Goal:** Resolusi konflik jika dua model AI berbeda pendapat.
```text
SYSTEM: Sintesis hasil analisis. Berikan vonis akhir berdasarkan hierarki: Hukum > Kesejahteraan Rakyat > Administrasi.
```

---

## 5. Fitur Unggulan (UI/UX)

1.  **Battle Mode ⚔️:** Perbandingan *side-by-side* (Contoh: Rudy Mas'ud vs Dedi Mulyadi) dengan radar chart interaktif.
2.  **Perspective Presets:** Tombol cepat untuk mengubah bobot skor (Mode Anti-Korupsi vs Mode Pembangunan).
3.  **Timeline of Sentiment:** Grafik fluktuasi ICP berdasarkan peristiwa berita tertentu.
4.  **Evidence Explorer:** Modal transparan yang menunjukkan link berita asli di balik setiap angka.
5.  **Sentinel Status:** Indikator visual keamanan rekam jejak (Safe / Neutral / Warning).

---

## 6. Spesifikasi Halaman Frontend

### **1. Halaman Utama (Landing & Pencarian)**

Ini adalah pintu masuk utama. Fokusnya adalah kemudahan mencari data.

- **Hero Section:** Pesan kuat seperti "Pantau Janji, Tagih Realita."
- **Global Search Bar:** Cari nama pejabat (Rudy Mas'ud, Dedi Mulyadi, dll).
- **Trending Battle:** Box kecil yang memperlihatkan perbandingan yang sedang viral (misal: "Rudy vs Dedi").
- **Stats Overview:** Jumlah berita yang diolah, jumlah janji yang dilacak, dan skor rata-rata nasional.

### **2. Halaman Penjelajah (Direktori)**

Daftar semua pejabat agar user bisa melakukan browsing.

- **Filter & Sorting:** Berdasarkan wilayah (Kaltim, Jabar, DKI), jabatan (Gubernur, Menteri), atau skor ICP tertinggi/terendah.
- **Leaderboard:** Ranking pejabat berdasarkan axis tertentu (misal: "Paling Transparan" atau "Realisasi Janji Terbaik").

### **3. Halaman Detail Profil (The Deep Dive) — Halaman Paling Penting**

Halaman ini adalah "Rapor" lengkap dari satu pejabat.

- **Header:** Foto, jabatan, dan Skor ICP Utama.
- **Radar Chart:** Visualisasi 4 axis (Integritas, Janji, Efisiensi, Sosial).
- **AI Verdict:** Ringkasan singkat dari AI ("Chief Justice") tentang performa pejabat ini.
- **Promise Tracker Tab:** List janji kampanye beserta statusnya (Terwujud/Mangkrak).
- **News Timeline:** Grafik sentimen dari waktu ke waktu. Jika grafik turun, user bisa klik untuk lihat berita apa penyebabnya.

### **4. Halaman Perbandingan (The Battle Mode)**

Halaman khusus untuk membandingkan dua orang secara side-by-side.

- **Dual Radar Chart:** Dua grafik radar yang bertumpuk (overlay) untuk melihat perbedaan mencolok.
- **Juxtaposed Stats:** Tabel perbandingan (misal: Janji Rudy vs Janji Dedi).
- **AI Comparative Summary:** AI menganalisis siapa yang lebih unggul di bidang apa.
- **Perspective Switcher:** Tombol untuk ganti bobot (Mode Anti-Korupsi vs Mode Pembangunan).

### **5. Halaman Metodologi & Transparansi (The Legal Shield)**

Halaman ini sangat penting untuk membangun kepercayaan dan menghindari tuntutan hukum.

- **Formula Scoring:** Penjelasan bagaimana angka dihasilkan.
- **Data Sources:** List media massa yang di-scrape.
- **Ownership Mapping:** Penjelasan tentang sistem konsensus media (bagaimana kamu menangani bias media).
- **Right to Reply:** Formulir khusus untuk staf ahli pejabat yang ingin memberikan klarifikasi resmi.

### **Fitur Tambahan (Versi Pro)**

- **News Feed Page:** Live stream berita-berita terbaru yang baru saja dianalisis oleh AI secara real-time.
- **User Dashboard:** Jika ada fitur Login, user bisa "Follow" pejabat tertentu untuk dapat notifikasi jika ada berita baru atau perubahan skor rapor mereka.

### **Rekomendasi untuk Demo**

Karena target awalmu adalah Rudy Mas'ud dan Dedi Mulyadi, fokuslah pada Page 3 (Profile) dan Page 4 (Comparison). Dua halaman ini yang akan memberikan efek "Wow" paling besar saat presentasi atau demo.

---

## 7. Strategi Keamanan & Legal (Safe Harbor)

1.  **Neutrality Protocol:** Instruksi sistem melarang AI membuat kesimpulan tanpa bukti berita.
2.  **Official Disclaimer:** Platform bersifat agregator, bukan penentu kebenaran absolut.
3.  **Right to Reply (Verified):** Pejabat dapat memberikan klarifikasi resmi melalui email instansi (`.go.id`) yang akan ditampilkan di samping berita terkait.
4.  **No Adjectives Policy:** Menghindari delik pencemaran nama baik (UU ITE) dengan fokus pada data kuantitatif dan kutipan media massa terverifikasi.

---

## 8. Roadmap & Milestone

| Fase | Durasi | Milestone Utama |
| :--- | :--- | :--- |
| **Fase 1: Research** | 2 Minggu | Pengumpulan Visi-Misi & Setup Frontend Prototype. |
| **Fase 2: Backend** | 4 Minggu | Integrasi FastAPI, Scraper Pipeline, & Database PostgreSQL. |
| **Fase 3: AI/RAG** | 3 Minggu | Implementasi Qdrant, Logic Scoring, & Chatbot RAG. |
| **Fase 4: Audit** | 3 Minggu | Beta testing, audit bias pihak ketiga, & perbaikan legalitas. |

---

## 9. Daftar Tokoh MVP

*   **Regional:** Rudy Mas'ud, Dedi Mulyadi, Ridwan Kamil, Ganjar Pranowo, Anies Baswedan, Ahok.
*   **Nasional:** Joko Widodo, Prabowo Subianto, Sri Mulyani Indrawati.

---

**Diverifikasi oleh RaporPejabat Dev Team**  
*Platform ini dibangun untuk transparansi demokrasi Indonesia.* 🇮🇩
