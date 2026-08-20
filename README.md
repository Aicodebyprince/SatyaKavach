# SatyaKavach 🛡️

### Detect • Verify • Trust

**SatyaKavach** is a citizen-first, multimodal AI platform that detects deepfake and manipulated media across **images, videos, and audio** — and delivers a unified **Trust Score**, an evidence-backed explanation, and a recommended action.

> 🏆 Built for **Omnikon National Hackathon 2026** · Problem Statement `Omni_CyberTech_4` · Theme **CyberTech** · Team **Codeators**

---

## Why SatyaKavach

Deepfakes are no longer distinguishable by the naked eye.

- **500M+** deepfake videos/images circulate globally each year
- **3X faster** spread of manipulated media vs verified content
- **96%** of deepfakes contain manipulated faces

Existing tools are fragmented — image-only, video-only, or research-grade. **SatyaKavach is one unified verification layer.**

## Features

| | |
|---|---|
| 🎭 **Deepfake Face Detection** | EfficientNet + XceptionNet + Gemini Vision ensemble |
| 🎥 **Video Deepfake Detection** | TimeSformer + Video Swin Transformer (frame-level) |
| 🎙️ **AI Voice Clone Detection** | Wav2Vec2 + Whisper + spectrogram analysis |
| 🧠 **Unified Trust Score** | Multimodal Risk Engine → 0–100 score + verdict |
| 📋 **Explainable Evidence Report** | Gemini 2.5 plain-language, evidence-backed reasoning |
| 🔗 **Threat Intelligence** | VirusTotal, Google Safe Browsing, PhishTank |
| 🇮🇳 **Hindi-First PWA** | Citizen-friendly, mobile-first interface |
| 🚔 **I4C / 1930 Integration** | One-tap reporting of confirmed deepfakes |

## How It Works

```
Upload (Image/Video/Audio/Link) → Preprocessing → Multimodal AI Analysis
      → Risk Engine → Trust Score (0–100) → Evidence Report → Recommended Action
```

## Tech Stack

**Frontend** React.js · TypeScript · Tailwind CSS · PWA  
**Backend** FastAPI · REST · JWT · Async Workers · Risk Engine  
**AI** Gemini 2.5 · EfficientNet · XceptionNet · TimeSformer · Video Swin · Whisper · Wav2Vec2 · EasyOCR  
**Data** PostgreSQL · AWS S3 · Threat Intelligence Cache · Audit Logs  
**Infra** Docker · AWS EC2 · Nginx · HTTPS

## Datasets

FaceForensics++ · Celeb-DF v2 · DFDC · DeepFakeTIMIT · ASVspoof 2019 · FakeAVCeleb · WaveFake · DeepFakeBench

## Documentation

| Document | Purpose |
|----------|---------|
| [`design.md`](./design.md) | System architecture & design |
| [`requirements.md`](./requirements.md) | Functional & non-functional requirements |
| [`features.md`](./features.md) | Feature catalogue & traceability |
| [`roadmap.md`](./roadmap.md) | Delivery phases & milestones |

## Roadmap

- **Phase A** — Hackathon MVP (48–72h): image/video/audio verification end-to-end
- **Phase B** — Public pilot: OCR, scam classifier, user accounts, I4C/1930 reporting
- **Phase C** — Nationwide scale: real-time video, admin dashboard, gov partnerships

## Team — Codeators

- **Prince Sherathiya**
- **Soham Shetye**

> *SatyaKavach: सत्य (truth) + कवच (armor) — armor for the truth.*

---

**License:** MIT · **Hackathon:** Omnikon 2026