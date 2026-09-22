# 🕸️ Ghost Networks
**Pan-African Job-Scam Network Detection System**  
Built for the **Apify x She Code Africa "BuildHer Hackathon"** (Cybersecurity Track)

---

## 💡 The Problem
In African job markets, deceptive job ads soliciting upfront "registration fees", "training kits", or "badge charges" are ubiquitous. Job seekers typically only view one ad in isolation, keeping the organized scale of these syndicates invisible. The same phone numbers, WhatsApp lines, and recycled templates cross borders—appearing simultaneously in Nigeria, Cameroon, and Kenya under dozens of fake company identities.

## 🎯 The Solution
**Ghost Networks** moves beyond flagging isolated ads. It aggregates job postings across platforms and countries, normalizes contact identifiers, detects recycled text templates using RapidFuzz, and constructs an **interactive graph via NetworkX and Pyvis** to expose multi-country scam syndicates.
Instead of *"this ad might be a scam"*, it shows:  
👉 **"This phone number appears in 14 fraudulent ads across Nigeria and Cameroon asking for registration fees."**

---

## 🏗️ Architecture & Stack
- **Scraping**: Apify Actors + `apify-client` (multi-platform extraction across CMR, NGA, KEN)
- **Backend & Detection**: Python + FastAPI + SQLAlchemy + `rapidfuzz` (text similarity) + `phonenumbers` (E.164 normalization)
- **Network Analysis**: NetworkX (connected components and syndicate community clustering)
- **Database**: PostgreSQL 15 (Dockerized)
- **Interactive UI**: Streamlit + Pyvis (dynamic network graph with node inspection)
- **Containerization**: Docker Compose (100% offline-capable, one-command bootstrapping)

```
Apify Scrapers (Multi-Country)
          │
          ▼
   FastAPI Backend ──► RapidFuzz + phonenumbers + NetworkX
          │                                  │
          ▼                                  ▼
    PostgreSQL DB ────────────────────► Streamlit Dashboard
                                        (Interactive Graph + Explainable Signals)
```

---

## 🚀 Quickstart (One Command)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) installed.

### 1. Clone & Configure
```bash
git clone https://github.com/your-org/ghost-networks.git
cd ghost-networks
cp .env.example .env
```

### 2. Boot the Entire System
```bash
docker-compose up --build
```

That's it! The system automatically:
1. Boots PostgreSQL and verifies database health.
2. Applies schemas and automatically seeds `data/seed/listings_sample.json` (pan-African ads with embedded scam rings).
3. Executes contact normalization, RapidFuzz similarity matching, explainable risk scoring, and NetworkX syndicate clustering.
4. Starts FastAPI backend on **`http://localhost:8000`**.
5. Starts Streamlit dashboard on **`http://localhost:8501`**.

---

## 🖥️ Live Service URLs
- **Interactive Dashboard:** [http://localhost:8501](http://localhost:8501)
- **FastAPI Interactive Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 👥 Team Split & Modules
- **Dev 1 (Scraper & Apify):** `scraper/` — Apify Actor manifests, extraction logic, raw text parsing.
- **Dev 2 (Backend & Detection):** `backend/` — Normalization, RapidFuzz matching, explainable 0–100 scoring engine, NetworkX graph service, and REST API.
- **Dev 3 (Dashboard & Demo):** `dashboard/` — Streamlit UI, Pyvis interactive graph canvas, KPI cards, and pitch scenario.

---

## 🛡️ Explainable Risk Scoring Engine (0–100)
Risk scores are deterministic and accompanied by a human-readable one-sentence explanation:
- **Cross-Border Contact (+35 pts):** Same contact phone/email detected in multiple countries.
- **Reused Phone Syndicate (+30 pts):** Phone number shared across $\ge 3$ distinct job ads.
- **Recycled Text Template (+25 pts):** RapidFuzz token set similarity $\ge 85\%$ against another recruiter.
- **Fee Solicitation (+25 pts):** Detects explicit demands for *registration fee, badge fee, training kit, frais de dossier*.
- **Email Syndicate (+20 pts):** Contact email shared across multiple ads.
- **Free Corporate Webmail (+10 pts):** Corporate recruiter relying on a free `@gmail.com` address.
