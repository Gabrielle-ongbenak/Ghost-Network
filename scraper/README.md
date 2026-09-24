# 🕸️ Pan-African Job Scam & Threat Network Detector

> **Built for the Apify x SCA BuildHer 2026 Hackathon**  
> *Theme: Ship and Earn Africa | Track: Cybersecurity & Threat Intelligence*

An advanced Apify Actor that audits African job postings (Cameroon, Nigeria, Kenya), normalizes phone and WhatsApp identifiers, detects illegal upfront fee demands, and unmasks **cross-border scam syndicates** using graph intelligence (NetworkX).

---

## 💡 The African Context & Problem
In African job markets, deceptive job ads soliciting upfront **"registration fees"**, **"frais de dossier"**, **"training kits"**, or **"badge charges"** prey on vulnerable job seekers. 
Because job seekers and boards view postings in isolation, the coordinated scale of these criminal rings remains hidden. The **same WhatsApp lines, mobile numbers, and recycled templates cross national borders**—appearing simultaneously in Douala, Lagos, and Nairobi under dozens of fictional company identities.

This Actor moves beyond simple keyword matching:
👉 **It reconstructs the hidden web of interconnected recruiters and exposes transnational fraud rings.**

---

## ✨ Features
- 🌍 **Multi-Country Coverage:** Scans and correlates listings across **Cameroon (CMR)**, **Nigeria (NGA)**, **Kenya (KEN)**, and **Ghana (GHA)**.
- 📱 **Robust Contact Extraction & E.164 Normalization:** Extracts phone numbers, WhatsApp lines, and emails via regex, standardizing them to international E.164 format via the `phonenumbers` library.
- 🛡️ **Explainable Risk Scoring Engine (0–100):** Assigns deterministic risk scores based on upfront fee solicitation, recruiter webmails (`@gmail.com`), and mismatched international phone prefixes.
- 🕸️ **NetworkX Graph Community Clustering:** Constructs a bipartite graph linking job ads through shared contact points and identifies connected components.
- 🚨 **Cross-Border Syndicate Detection:** Automatically tags rings operating across multiple countries with a maximum threat score of **100 (CRITICAL)**.

---

## 💰 Pay-Per-Event (PPE) Pricing

This Actor utilizes Apify's **Pay-Per-Event (PPE)** model so you only pay for actual intelligence delivered:

| Event Name | Unit Price (USD) | Description |
| :--- | :---: | :--- |
| **`LISTING_SCANNED`** | **$0.005** | Per job posting retrieved, contact-parsed, and audited for scam signals. |
| **`SYNDICATE_UNMASKED`** | **$0.05** | High-value threat event: triggered whenever an active cross-border criminal syndicate is unmasked. |

---

## 📥 Input Configuration

| Parameter | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `target_countries` | `array` | `["CMR", "NGA", "KEN"]` | African country codes to inspect. |
| `search_keywords` | `array` | `["assistant", "secretary", ...]` | Target job titles, industries, or suspicious keywords. |
| `max_listings` | `integer` | `30` | Maximum number of listings to collect and analyze. |
| `enable_network_analysis`| `boolean` | `true` | Enables NetworkX correlation and syndicate clustering. |
| `custom_listings` | `array` | `[]` | Optional JSON array of raw ads for instant custom batch auditing. |

### Example Input
```json
{
  "target_countries": ["CMR", "NGA"],
  "search_keywords": ["receptionist", "frais de dossier", "registration fee"],
  "max_listings": 20,
  "enable_network_analysis": true
}
```

---

## 📤 Output Data

The Actor stores results directly in the default Apify Dataset:

### 1. Job Listing Audit (`record_type: "JOB_LISTING"`)
```json
{
  "record_type": "JOB_LISTING",
  "source_id": "jiji_nga_101",
  "title": "Administrative Assistant Urgently Needed",
  "platform": "jiji",
  "country_code": "NGA",
  "poster_name": "Global Career Recruiters Ltd",
  "contacts": [
    { "type": "PHONE", "raw": "08031234567", "normalized": "+2348031234567", "country": "NGA" },
    { "type": "EMAIL", "raw": "globalcareersonline@gmail.com", "normalized": "globalcareersonline@gmail.com", "country": "NGA" }
  ],
  "risk_score": 100,
  "risk_level": "CRITICAL",
  "risk_signals": [
    { "code": "FEE_SOLICITATION", "points": 25, "description": "Demande de frais d'inscription ou d'enregistrement ('registration fee')" },
    { "code": "FREE_WEBMAIL_RECRUITER", "points": 10, "description": "Adresse email grand public utilisée pour un recrutement d'entreprise" },
    { "code": "CROSS_BORDER_SYNDICATE", "points": 100, "description": "Membre d'un syndicat d'arnaque transfrontalier opérant entre CMR, NGA" }
  ],
  "syndicate_id": "syn_001",
  "syndicate_label": "Cross-Border Syndicate #1 (CMR-NGA Ring)"
}
```

### 2. Syndicate Threat Alert (`record_type: "SYNDICATE_ALERT"`)
```json
{
  "record_type": "SYNDICATE_ALERT",
  "syndicate_id": "syn_001",
  "label": "Cross-Border Syndicate #1 (CMR-NGA Ring)",
  "risk_score": 100,
  "is_cross_border": true,
  "listings_count": 4,
  "contacts_count": 3,
  "countries_involved": ["CMR", "NGA"],
  "platforms_involved": ["jiji", "facebook_group", "cameroon_classifieds"],
  "shared_contacts": [
    { "type": "PHONE", "value": "+2348031234567", "country": "NGA" },
    { "type": "EMAIL", "value": "globalcareersonline@gmail.com", "country": "NGA" }
  ]
}
```

---

## 🏢 Who is this for?
- **Online Job Boards (Jobberman, Jiji, etc.):** Automatically vet submitted ads and protect job seekers before publication.
- **Law Enforcement & Cyber Units:** Map transnational recruitment syndicates operating between West and Central Africa.
- **NGOs & Watchdogs:** Monitor and report youth employment exploitation.
