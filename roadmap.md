# Roadmap Document: SatyaKavach – AI-Powered Deepfake & Manipulated Media Detection

> **Connected Documents**: [features.md](./features.md) (feature catalogue & traceability) · [requirements.md](./requirements.md) (requirements & acceptance criteria) · [design.md](./design.md) (architecture & design)
>
> This roadmap defines how SatyaKavach is delivered — from a hackathon MVP to a nationwide verification platform. Each phase lists scope, features (FXX), requirements (FR-XX / NFR-XX), milestones, and success criteria.

## 1. Vision & Guiding Principles

**Vision**: A citizen-first, unified verification layer that helps everyone — citizens, journalists, educators, and institutions — detect deepfake and manipulated media with explainable, actionable results.

**Guiding Principles**
- **Citizen-First**: Deliver value to everyday users before enterprise features
- **Explainable at Every Step**: Every phase preserves evidence-backed verdicts
- **Data-Driven**: Gate every phase on measurable accuracy and adoption metrics
- **Modular by Design**: Features land in phases without re-architecture (modular AI services)
- **Security & Privacy by Default**: Applied from Phase A onward, never retrofitted

## 2. Roadmap Phases at a Glance

| Phase | Timeline | Objective | Key Features | Success Criteria |
|-------|----------|-----------|--------------|------------------|
| **A — Hackathon MVP** | 48–72 hours | Working multimodal verification demo | F1–F5, F8–F11, F13 | End-to-end demo with Trust Score + Evidence Report |
| **B — Public Pilot** | 1–3 months | Pilot deployment with OCR, scam detection, reporting | F6, F7, F12, F14 | 1,000+ verifications, 90%+ accuracy, 100% explainability |
| **C — Nationwide Scale** | 3–12 months | Scale to states; journalism & gov partnerships | F15 | 100K+ verifications, real-time video, I4C/1930 integration |
| **C+ — Intelligence & Ecosystem** | 12+ months | Trend monitoring, attribution, media literacy | Extensibility (design §12) | Government/media adoption, continuous benchmarking |

## 3. Phase A — Hackathon MVP (48–72 Hours)

### 3.1 Objective

Deliver a working, demoable platform that verifies images, videos, and audio with a **Unified Trust Score**, **Evidence Report**, and **Recommended Action**, in a Hindi-first PWA.

### 3.2 Scope

**In Scope** (all P0 features from [features.md](./features.md)):
- **F1** Multimodal Media Upload (image/video/audio/screenshot/link)
- **F2** Deepfake Face Detection (image)
- **F3** Video Deepfake Detection
- **F4** AI Voice Clone Detection
- **F5** Media Forensics Engine
- **F8** Threat Intelligence (link/URL)
- **F9** Unified Trust Score & Verdict
- **F10** Explainable Evidence Report
- **F11** Recommended Action
- **F13** Hindi-First Citizen Interface (PWA)

**Out of Scope (deferred to Phase B)**: F6 (OCR), F7 (Scam Classifier), F12 (I4C/1930), F14 (accounts), F15 (admin dashboard).

### 3.3 Requirements Covered

FR-01, FR-02, FR-03, FR-04, FR-05, FR-08, FR-09, FR-10, FR-11, FR-13 + NFR-16 (performance), NFR-18 (security), NFR-21 (reliability).

### 3.4 Build Milestones

| Milestone | Hours | Deliverable |
|-----------|-------|-------------|
| **M1 — Foundations** | 0–6 | FastAPI + React scaffold, PostgreSQL + S3 (MinIO), Docker Compose, upload endpoint |
| **M2 — Preprocessing** | 6–10 | Frame extraction, face crop/align, audio extraction, spectrogram generation |
| **M3 — Modal Detectors** | 10–18 | Image ensemble, video detectors, audio detectors (modular AI services) |
| **M4 — Fusion & Reasoning** | 18–24 | Risk Engine, Gemini 2.5 evidence report, threat-intel integration |
| **M5 — Frontend** | 24–32 | Hindi-first PWA, upload flow, Trust Score gauge, evidence report view |
| **M6 — Hardening** | 32–40 | Error handling, audit logs, tests, demo datasets, SHA-256 dedup |
| **M7 — Demo Prep** | 40–48 | Scenario walkthroughs, performance pass, pitch materials |

### 3.5 Demo Scenarios

1. **Manipulated image** → LOW_TRUST (15/100) → Evidence Report with highlighted artifacts → "Do not share — report to I4C/1930"
2. **Authentic video** → HIGH_TRUST (92/100) → passing checks explained
3. **Suspicious link** → Threat Intelligence flags malicious URL → LOW_TRUST
4. **Voice-clone clip** → Audio Authenticity Score low → LOW_TRUST with transcript evidence

### 3.6 Success Criteria (Phase A)

- End-to-end demo completes for image, video, and audio in under 3 minutes each
- 100% of demo verifications produce a Trust Score + Evidence Report + Recommended Action
- Detection accuracy ≥ 90% on curated demo samples from DFDC / FaceForensics++ / ASVspoof
- PWA installs and runs on a mobile device; Hindi default UI

## 4. Phase B — Public Pilot (1–3 Months)

### 4.1 Objective

Evolve the MVP into a pilot-ready platform with text/scam analysis, user accounts, and civic reporting — and validate accuracy, explainability, and adoption with real users.

### 4.2 Scope

**New Features**:
- **F6** OCR Text Extraction (EasyOCR)
- **F7** NLP / Scam Intent Classifier
- **F12** I4C / 1930 Reporting & Audit
- **F14** User Accounts, JWT Auth & Verification History

**Enhancements**:
- Multi-language evidence reports (Tamil, Telugu, Bengali)
- Journalist / fact-checker workflows and evidence export
- Real threat-intel API integration with Threat Intelligence Cache (TTL)
- Batch verification support

### 4.3 Requirements Covered

Adds FR-06, FR-07, FR-12, FR-14 + NFR-17 (scalability), NFR-19 (accessibility), NFR-20 (maintainability).

### 4.4 Pilot Plan

| Week | Activity |
|------|----------|
| 1–2 | OCR + Scam Classifier integration; user accounts; audit + reporting stubs |
| 3–4 | I4C/1930 report export; threat-intel cache tuning; multi-language content |
| 5–6 | Closed pilot with journalists, fact-checkers, and community volunteers |
| 7–8 | Expand to 1,000+ verifications; collect accuracy and satisfaction feedback |
| 9–12 | Analyze data; refine models (DeepFakeBench); prepare Phase C |

### 4.5 Success Criteria (Phase B)

- 1,000+ successful verifications across all modalities
- 90%+ detection accuracy; < 5% FALSE_TRUST on benchmark samples
- 100% explainability (every verdict has an Evidence Report)
- OCR/scam detection correctly flags known phishing screenshots
- I4C/1930 report export works end-to-end with audit trail
- Median verdict time: image < 10s, video < 60s, audio < 30s

## 5. Phase C — Nationwide Scale (3–12 Months)

### 5.1 Objective

Scale the platform nationally, enable real-time verification, add the admin dashboard, and establish government/media partnerships.

### 5.2 Scope

**New Features**:
- **F15** Moderator / Admin Dashboard

**Enhancements**:
- Real-time / streaming video verification
- Multi-region deployment and auto-scaling
- Public API for journalist bulk verification
- Government (MeitY / Digital India alignment) and media partnerships
- I4C / 1930 bidirectional integration

### 5.3 Requirements Covered

Adds FR-15 + NFR-17 (scale) at production grade; full NFR compliance.

### 5.4 Milestones

| Month | Milestone |
|-------|-----------|
| 3–4 | Admin dashboard, real-time video, public API |
| 5–6 | Multi-region deployment, auto-scaling, media partnerships |
| 7–8 | Government / MeitY alignment, I4C/1930 bidirectional integration |
| 9–12 | Nationwide promotion, media-literacy campaigns |

### 5.5 Success Criteria (Phase C)

- 100K+ verifications; 99.5% uptime
- Real-time video verdicts under 5 seconds
- Public API serving journalist/fact-checker bulk workflows
- I4C/1930 bidirectional reporting operational
- Government and media partnerships formalized

## 6. Phase C+ — Intelligence & Ecosystem (12+ Months)

### 6.1 Objective

Turn SatyaKavach into a living intelligence layer against evolving deepfake threats, supporting responsible-AI adoption (see [design.md](./design.md) §12).

### 6.2 Planned Enhancements

- **Deepfake Trend Monitoring**: detect hotspots and emerging manipulation techniques
- **Misinformation Event Alerts**: flag upload spikes correlated with viral campaigns
- **Synthetic Media Attribution**: fingerprint the generating model
- **Real-Time / Broadcast Verification**: live video and broadcast clips
- **Media Literacy**: educator tools and campaign integrations
- **Continuous Benchmarking**: automated retraining/eval against DeepFakeBench and new datasets

### 6.3 Success Criteria (Phase C+)

- Trend/attribution dashboards operational
- Automated model retraining pipeline with drift detection
- Adoption in educational institutions and media literacy programs
- Recognition within Digital India / trustworthy-AI initiatives

## 7. Dependencies & Sequencing

| This Depends On | Deliverable | Unblocks |
|-----------------|-------------|----------|
| Design (design.md §3) | Component architecture | Phase A build |
| Datasets (DFDC, FF++, Celeb-DF v2, ASVspoof) | Trained/evaluated models | Phase A detectors |
| Threat-intel APIs (VirusTotal, Safe Browsing, PhishTank) | Link verification | Phase A F8 |
| Gemini API (Vision + 2.5) | Image corroboration + explainability | Phase A F2, F10 |
| EasyOCR + Whisper | OCR + transcription | Phase B F6, F4 enhancement |
| User accounts (F14) | Auth + history | Phase B reporting |
| I4C/1930 ecosystem | Civic reporting | Phase B F12 |
| Admin dashboard (F15) | Ops visibility | Phase C |
| Real-time video pipeline | Streaming verification | Phase C |

## 8. Metrics & Milestone Gate Review

Each phase gates on measurable success criteria. Gate review checklist:

- [ ] Detection accuracy maintained (≥ 90% on benchmarks)
- [ ] Explainability preserved (100% verdicts with Evidence Report)
- [ ] Performance targets met (image < 10s, video < 60s, audio < 30s)
- [ ] Security & privacy controls validated (encryption, RBAC, audit logs, retention)
- [ ] Graceful degradation verified (single-service failure still yields a verdict)
- [ ] Adoption targets met (verifications, satisfaction)

## 9. Risks to Roadmap & Mitigation

| Risk | Phase | Mitigation |
|------|-------|------------|
| Detection accuracy drift on new deepfakes | B, C | Ensembles, Gemini corroboration, DeepFakeBench benchmarking, UNCERTAIN zone |
| Threat-intel API quotas during pilot | B | Threat Intelligence Cache with TTL, multi-vendor fusion, graceful degradation |
| Cloud cost at scale | C | Stateless services, SHA-256 dedup, S3 lifecycle rules, modular scaling |
| Low citizen adoption | B | Hindi-first PWA, voice/screenshot/message/link intake, one-tap reporting |
| Privacy concerns | All | Anonymous access, metadata stripping, encryption, 90-day retention, audit logs |
| Regulatory changes (data protection) | C | Privacy-by-default design, DPDP alignment, consent-first storage |

## 10. Feature Delivery Summary

| Feature | Phase A | Phase B | Phase C | Phase C+ |
|---------|:-------:|:-------:|:-------:|:--------:|
| F1 Multimodal Media Upload | ✅ | | | |
| F2 Image Deepfake Detection | ✅ | | | |
| F3 Video Deepfake Detection | ✅ | | | |
| F4 Voice Clone Detection | ✅ | | | |
| F5 Media Forensics Engine | ✅ | | | |
| F6 OCR Text Extraction | | ✅ | | |
| F7 Scam Intent Classifier | | ✅ | | |
| F8 Threat Intelligence | ✅ | | | |
| F9 Unified Trust Score | ✅ | | | |
| F10 Evidence Report | ✅ | | | |
| F11 Recommended Action | ✅ | | | |
| F12 I4C/1930 Reporting | | ✅ | | |
| F13 Hindi-First PWA | ✅ | | | |
| F14 Accounts & History | | ✅ | | |
| F15 Admin Dashboard | | | ✅ | |
| Real-time video | | | ✅ | |
| Trend monitoring / attribution | | | | ✅ |

---

**Document Version:** 1.0  
**Last Updated:** August 2026  
**Status:** Ready for Hackathon Submission