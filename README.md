# 🕸️ Ghost Networks
**Pan-African Job-Scam & Threat Network Detection System**  
Built for the **Apify x SCA BuildHer 2026 Hackathon** (*Theme: Ship and Earn Africa* | *Cybersecurity Track*)

[![Apify Actor](https://img.shields.io/badge/Apify%20Store-Actor%20Ready-orange?logo=apify)](scraper/)
[![Monetization](https://img.shields.io/badge/Monetization-Pay--Per--Event%20(PPE)-brightgreen)](scraper/.actor/actor.json)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-teal?logo=fastapi)](https://fastapi.tiangolo.com/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.2.1-red)](https://networkx.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose%20Ready-blue?logo=docker)](https://www.docker.com/)

---

## 💡 The African Context & Problem
In African job markets, deceptive job ads soliciting upfront **"registration fees"**, **"frais de dossier"**, **"training kits"**, or **"badge charges"** exploit millions of job seekers annually.
Because job seekers and job boards evaluate postings in silos, the coordinated scale of these syndicates remains invisible. The **same WhatsApp lines, mobile numbers, and recycled templates cross national borders**—appearing simultaneously in Nigeria, Cameroon, and Kenya under dozens of fake corporate identities.

## 🎯 The Solution: Ghost Networks
**Ghost Networks** moves beyond flagging isolated ads:
1. **Audits job postings** across multiple African platforms (Jiji, Facebook groups, classifieds).
2. **Normalizes contact identifiers** to international E.164 format (`+237...`, `+234...`, `+254...`).
3. **Detects recycled text templates and illegal fee solicitation** via deterministic, explainable risk scoring.
4. **Constructs an interactive correlation graph via NetworkX** to unmask connected fraud rings operating across borders.

Instead of *"this ad might be a scam"*, it proves:  
👉 **"This phone number appears in 4 fraudulent ads across Cameroon and Nigeria demanding 15,000 FCFA registration fees (Syndicate Threat Score: 100/100 CRITICAL)."**

---

## 💰 Monetized Apify Actor (Pay-Per-Event)

Our standalone Apify Actor, **[`pan-african-job-scam-detector`](scraper/)**, is fully containerized and configured for publishing on the **Apify Store** with native **Pay-Per-Event (PPE)** monetization:

| PPE Event | Unit Price (USD) | Description |
| :--- | :---: | :--- |
| **`LISTING_SCANNED`** | **$0.005** | Billed per job ad collected, phone/email parsed, and risk-analyzed. |
| **`SYNDICATE_UNMASKED`** | **$0.05** | High-value threat event: billed whenever a cross-border criminal syndicate is identified. |

### Actor Specifications:
- **Manifest:** [`.actor/actor.json`](scraper/.actor/actor.json)
- **Input Schema:** [`.actor/input_schema.json`](scraper/.actor/input_schema.json)
- **Base Image:** `apify/actor-python:3.11`
- **Output:** Pushes structured records to Apify Default Dataset & executive audit report to Key-Value Store `OUTPUT`.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Apify Store: Actor Runtime                  │
│       (pan-african-job-scam-detector with PPE Monetization) │
│                                                             │
│  - Multi-Country Scraper & Ingestion (CMR, NGA, KEN)        │
│  - E.164 Contact Normalization & Regex Extraction          │
│  - NetworkX Connected Components & Cross-Border Detection   │
│  - Pay-Per-Event Billing: Actor.charge()                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Dataset / REST / Webhook)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Intelligence Backend               │
│                                                             │
│  - POST /api/ingest/apify (Remote Trigger / Sync)           │
│  - POST /api/ingest/run-detection (Global Graph Clustering) │
│  - GET  /api/networks (Syndicate Threat Registry)           │
│  - GET  /api/graph (Nodes & Edges for Visualizers)          │
│  - PostgreSQL 15 (Relational Store & Graph Junctions)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/)
- Python 3.11+ / Node 18+ (for Apify CLI)

### 1. Run the Backend & Database (Docker Compose)
```bash
# Clone the repository
git clone https://github.com/Gabrielle-ongbenak/Ghost-Network.git
cd Ghost-Network

# Setup environment
cp .env.example .env

# Boot PostgreSQL and FastAPI
docker compose up -d --build
```

- **Interactive API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

### 2. Test the Apify Actor Locally (Docker)
```bash
# Build the official Apify Actor container
docker build --network host -t ghost-networks-actor ./scraper

# Run the Actor in standalone mode
docker run --rm ghost-networks-actor
```

### 3. Deploy & Publish the Actor to Apify Store
```bash
cd scraper

# Login to your Apify account
npx apify-cli login

# Push the Actor to the Apify Store
npx apify-cli push
```

---

## 🛡️ Explainable Risk Scoring Engine (0–100)

Risk scores are deterministic and accompanied by human-readable signal explanations:
- **Cross-Border Syndicate (+100 pts / CRITICAL):** NetworkX detects the same contact ring operating across multiple countries (e.g. Cameroon & Nigeria).
- **Cross-Border Contact (+35 pts):** Mismatched foreign phone prefix used for a local classified ad.
- **Reused Phone Syndicate (+30 pts):** Identical phone number shared across $\ge 3$ distinct job postings.
- **Recycled Text Template (+25 pts):** Token similarity $\ge 85\%$ against another recruitment ad.
- **Fee Solicitation (+25 pts):** Explicit demands for *registration fee, badge fee, training kit, frais de dossier*.
- **Email Syndicate (+20 pts):** Contact email shared across multiple ads.
- **Free Corporate Webmail (+10 pts):** Corporate recruiter relying on a free `@gmail.com` address.

---

## 📂 Repository Structure

- **[`scraper/`](scraper/)**: The official Apify Actor module (manifest, input schema, Dockerfile, requirements, and execution code).
  - [`.actor/actor.json`](scraper/.actor/actor.json): Apify metadata and Pay-Per-Event (PPE) pricing specification.
  - [`.actor/input_schema.json`](scraper/.actor/input_schema.json): UI input form schema for Apify Store users.
  - [`src/main.py`](scraper/src/main.py): Async runtime orchestrating extraction, graph analysis, and `Actor.charge()`.
  - [`src/extractor.py`](scraper/src/extractor.py): Regex & E.164 phone normalizer.
  - [`src/network.py`](scraper/src/network.py): NetworkX graph builder and syndicate clustering.
  - [`src/data_loader.py`](scraper/src/data_loader.py): Pan-African scam dataset loader.
- **[`backend/`](backend/)**: FastAPI backend, database models, detection pipeline, and REST API.
  - [`app/routers/ingest.py`](backend/app/routers/ingest.py): Endpoints `/api/ingest/apify`, `/api/ingest/bulk`, `/api/ingest/run-detection`.
  - [`app/services/network_analyzer.py`](backend/app/services/network_analyzer.py): Backend graph analysis service.
  - [`app/services/apify_service.py`](backend/app/services/apify_service.py): Connector to execute Apify actors remotely.
- **[`data/seed/`](data/seed/)**: Seed archives of African scam advertisements and multilingual keyword dictionaries.
- **[`frontend/`](frontend/)**: Web dashboard interface workspace.

---

## 👥 Hackathon Submission Checklist

- [x] **Standalone Apify Actor:** Implemented in `scraper/` with `apify/actor-python:3.11`.
- [x] **Pay-Per-Event (PPE) Monetization:** Configured in `.actor/actor.json` & executed with `Actor.charge()`.
- [x] **Cybersecurity Theme & African Context:** Focus on Cameroon, Nigeria, Kenya job scams and cross-border threat syndicates.
- [x] **NetworkX Graph Intelligence:** Bipartite graph correlation linking listings and contacts.
- [x] **Public GitHub Repository:** Cleanly organized, documented, and reproducible.
