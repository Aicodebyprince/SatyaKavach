<div align="center">

<img src="frontend/public/favicon.svg" width="72" alt="SatyaKavach Logo"/>

# 🛡️ SatyaKavach — सत्य कवच

### *Armor for the Truth* — AI-Powered Deepfake & Manipulated Media Detection

**One unified platform where any citizen can verify images, videos, audio, screenshots, or suspicious links — and receive an explainable Trust Score in seconds.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Omnikon National Hackathon 2026 · Problem `Omni_CyberTech_4` · Team Codeators**

[🚀 Quick Start](#-quick-start) · [📸 Screenshots](#-screenshots) · [🏛️ Architecture](#%EF%B8%8F-system-architecture) · [🔌 API Docs](#-api-reference) · [🗺️ Roadmap](#%EF%B8%8F-roadmap)

</div>

---

## 📖 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Key Features](#-key-features)
- [Screenshots](#-screenshots)
- [System Architecture](#%EF%B8%8F-system-architecture)
- [AI Models & Detection Pipeline](#-ai-models--detection-pipeline)
- [Risk Engine & Trust Score](#%EF%B8%8F-risk-engine--trust-score)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Demo Mode](#-demo-mode)
- [Deployment](#-deployment-100-free-tier)
- [Roadmap](#%EF%B8%8F-roadmap)
- [Team](#-team)
- [Acknowledgements](#-acknowledgements)

---

## 🚨 The Problem

> Generative AI can now create **highly realistic fake images, videos, and voices** that are nearly impossible for ordinary users to distinguish from authentic content.

| ⚠️ Threat | 💥 Impact |
|---|---|
| 📈 **500M+ deepfakes** expected to circulate globally each year | Mass misinformation at unprecedented scale |
| ⚡ Fake media spreads **3× faster** than verified content | Damage done before fact-checkers can respond |
| 🎭 **96%** of deepfakes contain manipulated faces | Impersonation, fraud, blackmail, reputational harm |
| 🧩 Existing detection tools are **fragmented & research-grade** | Ordinary citizens have no accessible way to verify |

**Who faces this?** Social media users · Journalists & fact-checkers · Students & educators · Government institutions — essentially *anyone consuming digital content*.

---

## 💡 The Solution

**SatyaKavach** (सत्य = Truth + कवच = Armor) is a citizen-first AI verification platform that helps people verify suspicious digital content **before they act on it**.

```
Upload anything suspicious → Parallel multimodal AI analysis → One Trust Score → Explainable evidence report (Hindi-first) → Recommended action
```

<div align="center">
<img src="docs/screenshots/01-home-hindi.png" width="800" alt="SatyaKavach Homepage — Hindi"/>
<p><em>Hindi-first citizen interface — built for every Indian user</em></p>
</div>

### What makes it different?

| Pillar | How |
|---|---|
| 🔀 **Multimodal** | Image + Video + Audio + Links verified in one platform |
| 🔍 **Explainable** | Every verdict ships with evidence artifacts and per-model findings — never a black-box score |
| 🎯 **Action-oriented** | Clear recommendation: verify / do not share / report to **I4C / Cyber 1930** |
| 🇮🇳 **Hindi-first** | Full bilingual UI designed for Bharat-first adoption |
| 🛡️ **Privacy-first** | Encrypted storage, SHA-256 deduplication, immutable audit trail |

---

## ✨ Key Features

| # | Feature | Status | Description |
|---|---|---|---|
| F1 | 📤 Multimodal Upload | ✅ Built | Drag-&-drop images/video/audio, screenshots, or paste a link |
| F2 | 🖼️ Image Deepfake Detection | ✅ Built | EfficientNet + XceptionNet + Gemini Vision fusion |
| F3 | 🎬 Video Deepfake Detection | ✅ Built | Frame extraction → TimeSformer / Video Swin analysis |
| F4 | 🎙️ Voice Clone Detection | ✅ Built | Whisper transcription + Wav2Vec2 + spectrogram analysis |
| F5 | 🔬 Media Forensics Engine | ✅ Built | Tampering, splicing & editing artifact detection |
| F8 | 🌐 Threat Intelligence | ✅ Built | VirusTotal + Google Safe Browsing + PhishTank + domain reputation |
| F9 | ⚖️ Unified Trust Score | ✅ Built | Weighted risk fusion → 0–100 score + 3-tier verdict |
| F10 | 📋 Explainable Evidence Report | ✅ Built | Gemini-written, cites artifacts, Hindi-first templates |
| F11 | 🚨 Recommended Action | ✅ Built | Verify / do-not-share guidance incl. I4C/1930 reporting |
| F12 | 🔐 Accounts & History | ✅ Built | JWT auth, RBAC roles, anonymous sessions, verification history |
| F13 | 📱 Hindi-First PWA | ✅ Built | Installable, mobile-first, offline-tolerant UI |

---

## 📸 Screenshots

<table>
<tr>
<td width="50%">
<img src="docs/screenshots/02-home-english.png" alt="English homepage"/>
<p align="center"><strong>Landing Page (EN)</strong> — cinematic hero, live stats, upload zone</p>
</td>
<td width="50%">
<img src="docs/screenshots/03-results-trust-score.png" alt="Trust Score results page"/>
<p align="center"><strong>Verification Results</strong> — animated Trust Score gauge, verdict badge, model breakdown bars, evidence artifacts & recommended action</p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/screenshots/04-verification-history.png" alt="Verification history"/>
<p align="center"><strong>Verification History</strong> — past scans with scores & verdicts</p>
</td>
<td width="50%">
<img src="docs/screenshots/05-login-page.png" alt="Login page"/>
<p align="center"><strong>Authentication</strong> — secure JWT sessions (+ anonymous mode)</p>
</td>
</tr>
<tr>
<td colspan="2">
<img src="docs/screenshots/07-api-docs-swagger.png" alt="Swagger API docs"/>
<p align="center"><strong>Interactive API Documentation</strong> — auto-generated OpenAPI/Swagger at <code>/docs</code></p>
</td>
</tr>
</table>

<details>
<summary><strong>More screenshots</strong> (click to expand)</summary>

| | |
|---|---|
| ![Register](docs/screenshots/06-register-page.png) | *Account registration* |

</details>

---

## 🏛️ System Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                     1 · PRESENTATION LAYER                            │
│        React 18 + TypeScript PWA · Hindi-first · Tailwind CSS         │
└──────────────────────────────┬────────────────────────────────────────┘
                               │ REST API · JWT
┌──────────────────────────────▼────────────────────────────────────────┐
│                 2 · BACKEND & ORCHESTRATION                           │
│   FastAPI · Upload validation · Async job pipeline · RBAC · Audit     │
└───────┬──────────────────────────────┬────────────────────────────────┘
        │                              │
┌───────▼───────────────┐   ┌──────────▼───────────────────────────────┐
│  3 · AI & INTELLIGENCE │   │  4 · DATA LAYER                          │
│  ───────────────────── │   │  ───────────────────────────────────────  │
│  Image Detectors       │   │  PostgreSQL — users·uploads·verdicts     │
│  Video Pipeline        │   │  S3/R2/Local — encrypted evidence store  │
│  Audio Analysis        │   │  Threat Intel Cache — TTL'd results      │
│  OCR + Scam Classifier │   │  Audit Logs — immutable event trail      │
│  Gemini 2.5 Reasoning  │   │                                          │
└───────┬───────────────┘   └──────────────────────────────────────────┘
        │
┌───────▼───────────────────────────────────────────────────────────────┐
│                    5 · THREAT INTELLIGENCE                             │
│      VirusTotal · Google Safe Browsing · PhishTank · Domain Rep        │
└────────────────────────────────────────────────────────────────────────┘

  🔒 SECURITY FIRST — HTTPS · JWT · input validation · magic-byte checks
  ☁️  CLOUD READY    — Docker Compose · Nginx · stateless APIs
```

### Request lifecycle

```
POST /api/v1/upload/
  ├─ 1. Validate size ≤ 100MB, MIME type allow-list, SHA-256 dedup cache
  ├─ 2. Store original in object storage (S3/R2/local fallback)
  ├─ 3. Fan-out parallel analysis:
  │       image → EfficientNet ∥ XceptionNet ∥ Gemini Vision
  │       video → frame sampling → temporal models
  │       audio → Whisper transcript ∥ spectrogram ∥ Wav2Vec2
  │       link  → threat intel vendors (with TTL cache)
  ├─ 4. Risk Engine fuses available signals (weights re-normalized)
  ├─ 5. Gemini writes the explainable evidence report
  └─ 6. Persist verdict + audit log → return Trust Score
```

---

## 🧠 AI Models & Detection Pipeline

| Modality | Models | Datasets for Validation | Output |
|---|---|---|---|
| 🖼️ **Image** | EfficientNet-B4 · XceptionNet · Gemini Vision | FaceForensics++, Celeb-DF v2, DFDC | Manipulation score · fake/real class |
| 🎬 **Video** | TimeSformer · Video Swin Transformer | FaceForensics++, DFDC, DeepFakeTIMIT | Frame-level detection · authenticity score |
| 🎙️ **Audio** | Whisper · Wav2Vec2 · spectrogram CNN | ASVspoof 2019, FakeAVCeleb, WaveFake | Voice-clone detection · authenticity score |
| 🧩 **Fusion** | Weighted Risk Engine + Gemini 2.5 reasoning | — | Trust Score · evidence report · final verdict |

Every detector is a swappable service behind a common interface — mock engines power demo mode, real CPU/GPU implementations drop in without touching orchestration.

---

## ⚖️ Risk Engine & Trust Score

Signals are fused using configurable weights, **re-normalized over whichever signals are actually available** — so one failing analyzer never blocks a verdict:

```python
risk = Σ(weightᵢ × signalᵢ) / Σ(weightᵢ over available signals)

RISK_WEIGHT_IMAGE   = 0.30    # EfficientNet + XceptionNet + Gemini Vision
RISK_WEIGHT_VIDEO   = 0.25    # TimeSformer + Video Swin
RISK_WEIGHT_AUDIO   = 0.20    # Wav2Vec2 + spectrogram + Whisper
RISK_WEIGHT_OCR_NLP = 0.15    # EasyOCR + scam-message classifier
RISK_WEIGHT_THREAT  = 0.10    # VirusTotal + Safe Browsing + PhishTank
```

| Trust Score | Verdict | Meaning |
|---|---|---|
| `80 – 100` | 🟢 `HIGH_TRUST` | No manipulation signals found — likely authentic |
| `50 – 79` | 🟡 `UNCERTAIN` | Mixed signals — verify manually before sharing |
| `0 – 49` | 🔴 `LOW_TRUST` | High manipulation risk — do not share, consider reporting |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18 · TypeScript · Tailwind CSS · Vite · React Router · Axios · PWA |
| **Backend** | Python 3.11 · FastAPI · Uvicorn · SQLAlchemy 2 (async) · Pydantic v2 |
| **Auth** | JWT access+refresh tokens · bcrypt hashing · role hierarchy (`citizen→admin`) |
| **Database** | PostgreSQL 16 (prod) · SQLite async fallback (dev) · Alembic-ready |
| **Storage** | AWS S3-compatible (S3/R2/MinIO) · automatic local-disk dev fallback |
| **AI Services** | Pluggable detectors · Gemini 2.0 Flash client · mock engines |
| **Threat Intel** | VirusTotal API · Google Safe Browsing · PhishTank · TTL result cache |
| **Infra** | Docker Compose (api · postgres · minio · redis · nginx) · GitHub Actions CI |

---

## 📂 Project Structure

```
satyakavach/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory + lifespan
│   │   ├── core/
│   │   │   ├── config.py            # Typed settings (pydantic-settings)
│   │   │   ├── database.py          # Async SQLAlchemy engine & sessions
│   │   │   ├── security.py          # JWT · bcrypt · RBAC helpers
│   │   │   └── storage.py           # S3 storage w/ local dev fallback
│   │   ├── models/                  # User · MediaUpload · VerificationRecord
│   │   │                            # AuditLog · ThreatCache
│   │   ├── schemas/                 # Pydantic request/response models
│   │   ├── api/v1/
│   │   │   ├── auth.py              # register · login · anonymous · refresh
│   │   │   ├── upload.py            # POST /upload · /upload/link
│   │   │   ├── verification.py      # status · result · history
│   │   │   └── deps.py              # Auth dependencies
│   │   ├── services/
│   │   │   ├── ai/                  # image · video · audio detectors
│   │   │   ├── preprocessing/       # frame/face/audio extraction
│   │   │   ├── threat_intel/        # multi-vendor reputation service
│   │   │   ├── risk_engine.py       # ⭐ weighted signal fusion
│   │   │   └── verification.py      # pipeline orchestrator
│   │   └── workers.py               # Background job runner
│   ├── tests/
│   │   ├── unit/                    # Risk engine + detector tests
│   │   └── property/                # Hypothesis property-based tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/              # Navbar · TrustGauge · FileUpload · Icons
│   │   ├── pages/                   # Home · Results · History · Login · Register
│   │   ├── i18n/translations.ts     # Full हिंदी ⇄ EN dictionary
│   │   ├── services/api.ts          # Typed axios client + auto-anonymous auth
│   │   └── types/index.ts           # Shared TypeScript interfaces
│   └── public/                      # PWA manifest · icons
├── nginx/nginx.conf                 # Reverse proxy + TLS termination
├── docker-compose.yml               # api · postgres · minio · redis · nginx
├── docs/screenshots/                # Product screenshots
├── design.md                        # Full system design (~1,800 lines)
├── requirements.md                  # FR/NFR specifications
├── features.md                      # Feature catalogue & traceability
├── roadmap.md                       # Delivery phases A → C+
└── API_KEYS_GUIDE.md                # Free-tier key setup walkthrough
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| Docker *(optional)* | any recent |

### Option A — Local development (no Docker needed)

**1 · Backend**

```bash
cd backend
pip install -r requirements.txt

cp .env.example .env        # add your GEMINI_API_KEY (free @ ai.google.dev)

# Run with SQLite for instant local setup (no Postgres required):
DATABASE_URL="sqlite+aiosqlite:///./satya.local.db" uvicorn app.main:app --reload --port 8000
```

> ✅ The backend auto-creates tables, falls back to local-disk media storage when MinIO isn't running, and serves Swagger docs at [`http://localhost:8000/docs`](http://localhost:8000/docs).

**2 · Frontend**

```bash
cd frontend
npm install
npm run dev                 # → http://localhost:5173 (proxies /api → :8000)
```

### Option B — Full stack with Docker Compose

```bash
docker-compose up --build
# frontend  → http://localhost
# api       → http://localhost:8000
# minio     → http://localhost:9001
```

<details>
<summary><strong>⚙️ Environment variables</strong> (backend/.env)</summary>

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | recommended | Enables real Gemini Vision + evidence reports ([free key](https://ai.google.dev)) |
| `DEMO_MODE` | no | `true` → realistic mock AI scores; full flow needs zero keys |
| `DATABASE_URL` | no | Defaults to Docker Postgres; use SQLite locally (see above) |
| `JWT_SECRET_KEY` | prod | Change in production! |
| `VIRUSTOTAL_API_KEY` | optional | Live URL/file reputation (4 req/min free) |
| `GOOGLE_SAFE_BROWSING_API_KEY` | optional | Phishing URL checks (10k/day free) |
| `PHISHTANK_APP_KEY` | optional | Phishing database lookups |
| `S3_ENDPOINT` · `S3_ACCESS_KEY` · `S3_SECRET_KEY` | no | Object storage; local disk used when unreachable |

Full walkthrough: **[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)**

</details>

---

## 🔌 API Reference

Base URL: `/api/v1` · Interactive docs: `/docs` (Swagger) · `/redoc`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create account (email/phone + password) |
| `POST` | `/auth/login` | Obtain JWT access token |
| `POST` | `/auth/anonymous` | Instant guest session — zero friction |
| `POST` | `/upload/` | Multipart media upload → starts verification |
| `POST` | `/upload/link` | Submit suspicious URL for threat intel |
| `GET` | `/verification/{id}/status` | Job progress polling |
| `GET` | `/verification/{id}/result` | Full verdict: score · breakdown · evidence |
| `GET` | `/verification/history` | Paginated scan history (auth) |
| `GET` | `/health` | Service heartbeat |

**Example — verify an image:**

```bash
curl -X POST http://localhost:8000/api/v1/upload/ \
  -F "file=@suspicious_photo.jpg" \
  -F "language=hi"
```

```json
{
  "media_id": "7e2b0ff8-7063-4b3e-8932-e5604ceb50b4",
  "media_type": "image",
  "status": "complete",
  "message": "Verification complete"
}
```

**Example — fetch the verdict:**

```json
{
  "trust_score": 10,
  "verdict": "LOW_TRUST",
  "recommended_action": "High risk of manipulation detected. Do not share this media. Report to I4C/1930 if applicable.",
  "model_breakdown": {
    "image": {
      "manipulation_score": 0.9,
      "classification": "fake",
      "confidence": 0.85,
      "models": {
        "efficientnet_score": 0.9,
        "xceptionnet_score": 0.765,
        "gemini_vision_score": 0.855,
        "fusion_weights": { "efficientnet": 0.35, "xceptionnet": 0.35, "gemini_vision": 0.3 }
      },
      "artifacts": [
        "Face blending artifacts detected at jawline boundary",
        "Inconsistent skin texture across facial regions"
      ]
    }
  }
}
```

---

## 🧪 Testing

**27 automated tests** — unit + property-based (Hypothesis):

```bash
cd backend
pytest tests/unit -v          # Risk Engine & detector unit tests
pytest tests/property -v      # Correctness invariants (score bounds, weight re-normalization…)
pytest tests/ -v              # Everything
```

Property tests guarantee engine invariants such as: trust scores always within `[0, 100]`, weights always sum to `1.0` after re-normalization, and verdict thresholds are monotonic.

---

## 🎭 Demo Mode

Perfect for judges & quick demos — **no API keys required:**

| Setting | Behaviour |
|---|---|
| `DEMO_MODE=true` (default) | Realistic deterministic mock scores from every detector + full evidence reports |
| Add `GEMINI_API_KEY` | Reports become genuinely AI-generated while scores stay mocked |
| Production swap | Implementations of each detector service can be replaced with GPU-backed inference without touching orchestration |

---

## 🚢 Deployment (100% free tier)

| Component | Provider | Free tier |
|---|---|---|
| Frontend PWA | **Vercel / Netlify** | Unlimited static hosting + CDN |
| Backend API | **Render** | 750 hrs/month web service |
| Database | **Neon** | 0.5 GB serverless Postgres |
| Media storage | **Cloudflare R2** | 10 GB, zero egress fees |
| AI reasoning | **Google AI Studio** | Generous daily Gemini limits |
| Heavy models (optional) | **HF Spaces** | 2 vCPU · 16 GB RAM |

---

## 🗺️ Roadmap

| Phase | Timeline | Scope |
|---|---|---|
| ✅ **A — Hackathon MVP** | Done | Multimodal detection · Risk Engine · Evidence reports · Hindi PWA |
| 🔄 **B — Public Pilot** | Next 30 days | Free-stack deployment · OCR scam classifier · I4C/1930 reporting flow |
| 🔭 **C — Scale** | 3–12 months | Browser extension · WhatsApp bot intake · admin dashboard · regional languages |
| 🚀 **C+ — Platform** | 12+ months | Real-time video verification · trend monitoring · gov partnerships |

Detailed phase gates: **[roadmap.md](roadmap.md)** · Full spec: **[requirements.md](requirements.md)** · Design: **[design.md](design.md)**

---

## 👥 Team Codeators

| Member | Role |
|---|---|
| **Prince Sherathiya** | Full-stack & AI engineering |
| **Soham Shetye** | Product, research & testing |

*Built for the Omnikon National Hackathon 2026 — Problem `Omni_CyberTech_4` (CyberTech).*

---

## 🙏 Acknowledgements

- **Datasets:** [FaceForensics++](https://github.com/ondyari/FaceForensics) · [DFDC](https://ai.meta.com/datasets/dfdc) · [Celeb-DF v2](https://cse.buffalo.edu/~siweilyu/celeb-deepfakeforensics.html) · [ASVspoof 2019](https://www.asvspoof.org) · FakeAVCeleb · WaveFake · DeepFakeBench
- **Threat intelligence:** [VirusTotal](https://www.virustotal.com) · [Google Safe Browsing](https://safebrowsing.google.com) · [PhishTank](https://phishtank.org)
- **AI platform:** [Gemini API](https://ai.google.dev) · HuggingFace model ecosystem

## 📜 License

Released under the MIT License — see [LICENSE](LICENSE).

---

<div align="center">

**सत्य की रक्षा कवच** · *Armor for the Truth*

⭐ Star this repo if you believe in verifiable media!

</div>
