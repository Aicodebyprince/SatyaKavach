# Design Document: SatyaKavach – AI-Powered Deepfake & Manipulated Media Detection

## 1. Overview

SatyaKavach is a citizen-first, multimodal AI verification platform that helps people verify the authenticity of images, videos, and audio before acting on them. The system leverages deepfake detection models, AI forensics, and threat-intelligence signals to deliver a unified **Trust Score**, an evidence-based explanation, and a recommended action for every piece of uploaded media.

The platform addresses the rapid spread of manipulated media—500M+ deepfake videos and images are expected to circulate across digital platforms globally each year, and manipulated media spreads 3X faster than verified content. SatyaKavach is designed for social media users, journalists & fact-checkers, students & educators, and government & public institutions.

### 1.1 Design Principles

- **Citizen-First**: Accessible verification workflow for everyday users, not just researchers
- **Hindi-First**: Localized, bilingual (Hindi/English) interface for broad Indian reach
- **Multimodal**: One unified platform for image, video, and audio verification
- **Explainable AI**: Every verdict backed by evidence and confidence, never just a label
- **Action-Oriented**: Clear Trust Score plus a recommended next step
- **Secure-by-Design**: HTTPS, JWT, input validation, and secure file handling
- **Scalable**: Stateless APIs, asynchronous processing, and modular AI services
- **Cloud-Ready**: Docker, AWS EC2, AWS S3, Nginx deployment

### 1.2 Technology Stack

- **Frontend**: React.js + TypeScript, Tailwind CSS, PWA (installable, mobile-first)
- **Backend**: FastAPI (Python), REST APIs, JWT Authentication, Risk Engine
- **AI Models**: Gemini (Vision + 2.5), EfficientNet, XceptionNet, TimeSformer, Video Swin Transformer, Whisper, Wav2Vec2, EasyOCR
- **Storage**: PostgreSQL (users, reports, scores, history), AWS S3 (evidence/media), Threat Intelligence Cache
- **Threat Intelligence**: VirusTotal, Google Safe Browsing, PhishTank, Domain Reputation
- **Infrastructure**: Docker, AWS EC2, AWS S3, Nginx
- **Security**: HTTPS, JWT, Input Validation, Secure File Handling
- **Ecosystem**: I4C / 1930 integration for citizen cyber-fraud reporting

### 1.3 Problem Statement & Why It Matters

**Omnikon National Hackathon 2026 · Problem Statement: Omni_CyberTech_4 — Detecting Deepfake and Manipulated Media**

Generative AI can now create highly realistic fake images, videos, and voices that are difficult for ordinary users to distinguish from authentic content. Deepfakes are increasingly used to spread misinformation, impersonate individuals, manipulate public opinion, and damage trust in digital media.

**The Scale of the Threat**

| Signal | Insight |
|--------|---------|
| **500M+** | Deepfake videos and images expected to circulate across digital platforms globally each year |
| **3X FASTER** | Manipulated media spreads 3× faster than verified content |
| **96%** | Of detected deepfakes in public datasets contain manipulated faces |
| **MULTI-MODAL** | Verification needed across Image • Video • Audio in one unified platform |

*Sources: DFDC, FaceForensics++, FakeAVCeleb, DeepFakeBench*

**Who Is Affected**
- **Social media users** — first victims of manipulated media
- **Journalists & fact-checkers** — need fast, credible verification
- **Students & educators** — media literacy and academic integrity
- **Government & public institutions** — protecting official communication
- **Anyone consuming digital content**

**Key Insight**: People can no longer reliably distinguish authentic media from AI-generated content. The system must deliver **evidence-backed explanations, not just a "fake" or "real" label**.

### 1.4 Current Gap & Our Differentiation

Today's detection ecosystem is fragmented:

| Existing Solution | Limitation |
|-------------------|------------|
| Image tools | Image analysis only |
| Video tools | Video verification only |
| Audio tools | Voice-clone detection only |
| Research models | Difficult for citizens to use |

**The Gap**: Users need one simple platform that can verify images, videos, and audio with explainable results.

**SatyaKavach — One Unified Media Verification Layer**

| Pillar | How We Deliver |
|--------|----------------|
| **Multimodal** | Image + Video + Audio verification in one platform |
| **Explainable** | Shows evidence and confidence behind every detection |
| **Action-Oriented** | Clear trust score and verification recommendation |
| **Citizen-First** | Hindi-first, accessible, installable PWA experience |
| **Security-Aware** | Threat-intel enrichment + I4C/1930 fraud reporting ecosystem |

### 1.5 Alignment with India's Digital Ecosystem

SatyaKavach supports responsible AI adoption and complements existing digital trust initiatives:
- **MeitY initiatives** on trustworthy AI
- **Digital India mission**
- Citizen awareness against misinformation
- Media authenticity verification
- Explainable AI for public trust
- **I4C / 1930** citizen reporting & cyber-fraud support ecosystem

### 1.6 Evaluation Criteria Alignment

| Criterion | How SatyaKavach Addresses It |
|-----------|-------------------------------|
| **Problem Understanding** | Threat quantified (500M+, 3X spread, 96% faces) and the fragmentation gap clearly articulated |
| **Innovation & Creativity** | One unified multimodal verification layer with explainable, action-oriented verdicts |
| **Technical Complexity** | Multi-model ensembles, temporal video forensics, voice-clone detection, Gemini reasoning, threat-intel fusion |
| **Social Impact** | Protects citizens, journalists, educators, and institutions from misinformation and cyber-fraud |
| **Feasibility** | Proven open models + public datasets (DFDC, FaceForensics++, Celeb-DF v2, ASVspoof 2019, FakeAVCeleb, WaveFake) and a clear 48-hour MVP plan |
| **Presentation & Demo** | Five ready demo scenarios with a Hindi-first UI and evidence reports |

## 2. High-Level Architecture

### 2.1 Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Web    │  │   PWA    │  │  Voice   │  │  Hindi   │       │
│  │  Portal  │  │ (Mobile) │  │ Interface│  │   UI     │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│            React.js + TypeScript + Tailwind CSS                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND & ORCHESTRATION                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ FastAPI  │  │   REST   │  │   JWT    │  │  Risk    │       │
│  │  API     │  │  Endpoints│  │   Auth   │  │  Engine  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│              Stateless APIs • Async Processing                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   AI & INTELLIGENCE LAYER                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Image   │  │  Video   │  │  Audio   │  │Multimodal│       │
│  │ Deepfake │  │ Deepfake │  │ Deepfake │  │ Reasoning│       │
│  │ Detection│  │ Detection│  │ Detection│  │ (Gemini) │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐                                     │
│  │  EasyOCR │  │ NLP/Scam │  Detection, Reasoning,              │
│  │   Text   │  │Classifier│  Explainability                     │
│  │Extraction│  │          │                                     │
│  └──────────┘  └──────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  AWS S3  │  │ Threat   │  │  Audit   │       │
│  │(Reports, │  │(Evidence,│  │ Intelligence│  │  Logs   │       │
│  │ Scores,  │  │  Media)  │  │  Cache   │  │(Security)│       │
│  │  Users)  │  └──────────┘  └──────────┘  └──────────┘       │
│  └──────────┘                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              THREAT INTELLIGENCE & ECOSYSTEM                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │VirusTotal│  │ Google   │  │PhishTank │  │ I4C/1930 │       │
│  │  (URL/   │  │  Safe    │  │ (Phishing│  │ (Citizen │       │
│  │ File)    │  │ Browsing │  │   URL)   │  │Reporting)│       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Docker  │  │ AWS EC2  │  │  Nginx   │  │ AWS S3   │       │
│  │(Container)│  │(Compute) │  │(Reverse  │  │(Storage) │       │
│  │           │  │          │  │  Proxy)  │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│        HTTPS • Input Validation • Secure File Handling         │
└─────────────────────────────────────────────────────────────────┘
```

## 3. Detailed Component Architecture

### 3.1 Upload & Intake Service

**Purpose**: Accept media uploads (image, video, audio) and links from any channel, validate them securely, and queue them for analysis.

**Components**:

1. **File Upload Handler**
   - Accepts images (PNG, JPEG, WebP), videos (MP4, MOV, AVI), and audio (MP3, WAV, M4A)
   - Accepts URL/link submission for reputation analysis
   - Enforces file size limits and allowed MIME types
   - Streams files to AWS S3 for secure evidence storage
   - Generates a unique media ID and upload manifest

2. **Input Validation & Sanitization**
   - Validates file type, size, and integrity (magic-byte checks)
   - Strips metadata that could leak user location or device info
   - Rejects corrupt, oversized, or suspicious payloads
   - Sanitizes URLs before threat-intelligence lookup

3. **Security Scanning (VirusTotal)**
   - Scans uploaded files against known malware signatures
   - Checks URL/domain reputation for submitted links
   - Blocks known malicious payloads before AI analysis

4. **Async Job Queue**
   - Enqueues verification jobs asynchronously (stateless APIs)
   - Each job tracked with status: `queued → preprocessing → analyzing → scoring → complete`
   - Job state persisted so users can poll or receive notifications

**Upload Intake Schema**:
```typescript
interface MediaUpload {
  mediaId: string;              // Primary key (UUID)
  userId: string;
  mediaType: 'image' | 'video' | 'audio' | 'link' | 'screenshot';
  channel: 'web' | 'pwa' | 'voice' | 'message';
  sourceUrl?: string;
  s3Key: string;                // Secure evidence storage reference
  fileSizeBytes: number;
  mimeType: string;
  sha256: string;               // Content hash for deduplication
  language?: string;            // For OCR / transcription
  status: 'queued' | 'preprocessing' | 'analyzing' | 'scoring' | 'complete' | 'failed';
  createdAt: Date;
}
```

### 3.2 Media Preprocessing Service

**Purpose**: Normalize raw media into formats consumable by the AI detection models.

**Components**:

1. **Frame Extraction (Video)**
   - Extracts keyframes at configurable intervals (e.g., 1 frame/second)
   - Face detection and tracking across frames (96% of detected deepfakes contain manipulated faces)
   - Outputs frame-level samples for video deepfake models

2. **Audio Extraction (Video)**
   - Separates audio track from video
   - Converts to WAV format for Whisper/Wav2Vec2 analysis
   - Generates mel-spectrogram images for spectrogram-based detection

3. **Face Cropping & Alignment (Image/Video)**
   - Detects faces using face-detection models
   - Aligns and crops face regions for EfficientNet/XceptionNet
   - Tracks face identity across video frames

4. **Text Extraction (EasyOCR)**
   - Extracts embedded text from screenshots and images
   - Feeds OCR output to NLP/Scam Classifier for scam intent analysis
   - Preserves text bounding-box coordinates as evidence

5. **Audio Transcription (Whisper)**
   - Transcribes speech to text for scam/message intent analysis
   - Supports Hindi-first multilingual transcription
   - Outputs per-segment timestamps for evidence reports

**Preprocessing Pipeline**:
```
Raw Media Upload
     ↓
┌────────────────────────────────────────────────────────────┐
│ PREPROCESSING PIPELINE                                     │
│  Image  → Face detect/crop → aligned face tiles           │
│  Video  → Keyframe extraction → face tracking → tiles     │
│         → audio track extraction → WAV + spectrogram      │
│  Audio  → WAV conversion → mel-spectrogram → transcription│
│  Screen → EasyOCR text extraction → OCR boxes             │
│  Link   → URL/domain validation → threat intel lookup     │
└────────────────────────────────────────────────────────────┘
     ↓
  Feature artifacts (stored in S3 with evidence metadata)
```

### 3.3 Image Deepfake Detection Service

**Purpose**: Detect manipulated or AI-synthesized faces in images.

**Implementation**: Ensemble of EfficientNet + XceptionNet with Gemini Vision corroboration.

**Architecture**:
```
Aligned Face Tiles → EfficientNet → Fake probability (EfficientNet score)
                  → XceptionNet → Fake probability (XceptionNet score)
                  → Gemini Vision → Manipulation description + score
                       ↓
              Ensemble Fusion → Manipulation Score → Fake/Real Classification
```

**Ensemble Logic**:
```python
class ImageDeepfakeDetector:
    def analyze(self, face_tiles: List[Image], image_ctx: dict) -> ImageVerdict:
        efficientnet_scores = [self.efficientnet.predict(t) for t in face_tiles]
        xception_scores = [self.xceptionnet.predict(t) for t in face_tiles]
        gemini_analysis = self.gemini_vision.analyze_manipulation(image_ctx)

        fusion_score = (
            0.35 * mean(efficientnet_scores) +
            0.35 * mean(xception_scores) +
            0.30 * gemini_analysis.score
        )

        return ImageVerdict(
            manipulation_score=fusion_score,
            classification="fake" if fusion_score > 0.5 else "real",
            confidence=self.calc_confidence(efficientnet_scores, xception_scores),
            evidence=self.build_evidence(face_tiles, gemini_analysis)
        )
```

**Datasets Used for Training**: FaceForensics++, Celeb-DF v2, DFDC Dataset.

**Output**: Manipulation Score (0–1), Fake/Real Classification, per-face evidence.

### 3.4 Video Deepfake Detection Service

**Purpose**: Detect frame-level and temporal manipulation patterns in videos.

**Implementation**: TimeSformer + Video Swin Transformer with Gemini Vision frame verification.

**Architecture**:
```
Keyframes + Face Tracks → TimeSformer → Temporal manipulation score
                        → Video Swin Transformer → Frame-level scores
                        → Gemini Vision → Frame-by-frame verification
                              ↓
              Temporal Fusion → Video Authenticity Score → Frame-level Detection
```

**Temporal Consistency Logic**:
```python
class VideoDeepfakeDetector:
    def analyze(self, frames: List[Frame], face_tracks: List[Track]) -> VideoVerdict:
        time_scores = self.timesformer.predict(frames, face_tracks)
        swin_scores = self.swin_transformer.predict_frame_level(frames)
        gemini_verdicts = self.gemini_vision.verify_frames(frames)

        # Weight temporal coherence higher (interpolation artifacts)
        temporal_score = 0.40 * mean(time_scores) + 0.30 * mean(swin_scores)
        spatial_score = 0.30 * mean(gemini_verdicts)

        return VideoVerdict(
            video_authenticity_score=temporal_score + spatial_score,
            frame_level_detections=self.collect_frame_anomalies(swin_scores, frames),
            confidence=self.aggregate_confidence(...),
            evidence=self.build_frame_evidence(frames)
        )
```

**Datasets Used for Training**: FaceForensics++, DFDC Dataset, DeepFakeTIMIT.

**Output**: Frame-level Detection, Video Authenticity Score.

### 3.5 Audio Deepfake Detection Service

**Purpose**: Detect synthetic or cloned voices and assess audio authenticity.

**Implementation**: Whisper transcription signals + Wav2Vec2 embedding analysis + audio spectrogram analysis.

**Architecture**:
```
WAV + Mel-Spectrogram → Wav2Vec2 → Voice embedding / clone score
                     → Whisper → Transcription + audio signals
                     → Spectrogram Analysis → Artifact detection
                          ↓
              Audio Fusion → Voice Clone Detection → Audio Authenticity Score
```

**Audio Analysis Logic**:
```python
class AudioDeepfakeDetector:
    def analyze(self, wav: bytes, spectrogram: Image) -> AudioVerdict:
        wav2vec_embedding = self.wav2vec2.extract_embedding(wav)
        clone_score = self.wav2vec2.detect_voice_clone(wav2vec_embedding)
        whisper_signals = self.whisper.transcribe_with_signals(wav)
        spectrogram_score = self.spectrogram_analysis.detect_artifacts(spectrogram)

        authenticity_score = (
            0.45 * clone_score +
            0.30 * spectrogram_score +
            0.25 * whisper_signals.anomaly_score
        )

        return AudioVerdict(
            voice_clone_detected=authenticity_score > 0.5,
            audio_authenticity_score=authenticity_score,
            transcript=whisper_signals.text,
            evidence=self.build_audio_evidence(spectrogram, whisper_signals)
        )
```

**Datasets Used for Training**: ASVspoof 2019, FakeAVCeleb, WaveFake.

**Output**: Voice Clone Detection, Audio Authenticity Score, transcript evidence.

### 3.6 OCR & NLP Scam Classifier

**Purpose**: Extract text from screenshots and analyze message intent for scam indicators.

**Component 1: EasyOCR Text Extraction**
- Extracts embedded text from screenshots, images, and message captures
- Supports Hindi and English text
- Outputs text with bounding boxes for evidence visualization

**Component 2: NLP / Scam Classifier**
- Analyzes extracted text and transcriptions for scam/intent signals
- Detects urgency, financial asks, impersonation language
- Produces a scam-likelihood score fed into the Risk Engine

**NLP Classification Logic**:
```python
class ScamClassifier:
    def classify(self, text: str, context: dict) -> ScamVerdict:
        intent = self.intent_model.predict(text)          # message/intent analysis
        scam_signals = self.scam_heuristics.detect(text)  # urgency, money, OTP, impersonation
        risk = self.risk_combiner(intent, scam_signals, context)

        return ScamVerdict(
            intent=intent,
            scam_likelihood=risk,
            indicators=scam_signals.matched_indicators,
            evidence=self.build_text_evidence(text)
        )
```

### 3.7 Threat Intelligence Service

**Purpose**: Enrich analysis with external security signals for links, domains, and files.

**Components**:

1. **VirusTotal Integration**
   - URL/domain/file reputation lookup
   - Malware scanning of uploaded files
   - Returns detection ratio and vendor verdicts

2. **Google Safe Browsing Integration**
   - Known malicious URL detection
   - Phishing and malware URL classification

3. **PhishTank Integration**
   - Phishing URL intelligence
   - Validated phishing submissions

4. **Domain Reputation**
   - Additional URL risk signals (age, SSL, popularity, typosquatting)

**Threat Intelligence Logic**:
```python
class ThreatIntelligenceService:
    def analyze(self, media: MediaUpload) -> ThreatVerdict:
        if media.mediaType != 'link':
            return ThreatVerdict(not_applicable=True)

        virus_total = self.virus_total.check_url(media.sourceUrl)
        safe_browsing = self.safe_browsing.check_url(media.sourceUrl)
        phishtank = self.phishtank.check(media.sourceUrl)
        domain = self.domain_reputation.score(media.sourceUrl)

        threat_score = max(virus_total.score, safe_browsing.score,
                           phishtank.score, domain.score)

        return ThreatVerdict(
            threat_score=threat_score,
            sources=self.collect_verdicts(virus_total, safe_browsing,
                                          phishtank, domain),
            evidence=self.build_threat_evidence(...)
        )
```

**Caching**: Results stored in the Threat Intelligence Cache (PostgreSQL-backed) with TTL to avoid redundant lookups.

### 3.8 Multimodal Reasoning & Risk Engine

**Purpose**: Combine all AI signals into a unified confidence score and explainable verdict.

**Implementation**: FastAPI service orchestrating Gemini 2.5 reasoning over aggregated evidence.

**Architecture**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    RISK ENGINE                                  │
│  Image Verdict ──┐                                              │
│  Video Verdict ──┼──→ Signal Normalization → Weighted Fusion    │
│  Audio Verdict ──┤                  │                           │
│  OCR/NLP Verdict─┤                  ↓                           │
│  Threat Verdict ─┘        Unified Trust Score (0–100)           │
│                               │                                 │
│                               ↓                                 │
│              Gemini 2.5 Explainable Reasoning                   │
│              - Context understanding                            │
│              - Risk reasoning                                   │
│              - Evidence report generation                       │
│                               ↓                                 │
│         Trust Score • Evidence Report • Final Verdict           │
└─────────────────────────────────────────────────────────────────┘
```

**Risk Fusion Logic**:
```python
class RiskEngine:
    WEIGHTS = {
        'image': 0.30,
        'video': 0.25,
        'audio': 0.20,
        'ocr_nlp': 0.15,
        'threat': 0.10,
    }

    def compute_trust_score(self, signals: Dict[str, Verdict]) -> TrustResult:
        normalized = self.normalize_signals(signals)   # map each verdict to 0–1 risk
        available = {k: v for k, v in normalized.items() if v is not None}

        weighted_risk = sum(
            self.WEIGHTS[k] * v for k, v in available.items()
        ) / sum(self.WEIGHTS[k] for k in available)

        trust_score = round((1 - weighted_risk) * 100)

        verdict = self.map_verdict(trust_score)        # high / medium / low trust
        reasoning = self.gemini.reason(trust_score, available, self.evidence)

        return TrustResult(
            trust_score=trust_score,
            verdict=verdict,
            recommended_action=self.map_action(verdict),
            evidence_report=reasoning.report,
            model_breakdown=available
        )

    def map_verdict(self, score: int) -> str:
        if score >= 80: return "HIGH_TRUST"
        if score >= 50: return "UNCERTAIN"
        return "LOW_TRUST"

    def map_action(self, verdict: str) -> str:
        actions = {
            "HIGH_TRUST": "Likely authentic. Verify context before sharing.",
            "UNCERTAIN": "Further verification recommended. Cross-check the source.",
            "LOW_TRUST": "High risk of manipulation. Do not share; report to I4C/1930.",
        }
        return actions[verdict]
```

**Gemini 2.5 Explainable Layer**:
- Generates a plain-language explanation of why a verdict was reached
- Highlights the most influential signals (e.g., face blending artifacts, voice clone score, malicious URL)
- Produces the final Evidence Report with cited artifacts (frames, spectrograms, OCR boxes, vendor verdicts)

**Final Output**: Trust Score (0–100), Evidence Report, Final Verdict, Recommended Action.

### 3.9 User Management & Authentication

**Purpose**: Secure user accounts, sessions, and access control.

**Components**:

1. **JWT Authentication**
   - Stateless, signed access tokens with short expiry
   - Refresh tokens for extended sessions
   - Role-based claims (`citizen`, `journalist`, `moderator`, `admin`)

2. **User Service (FastAPI)**
   - Registration/login (email/phone + OTP or password)
   - Verification history per user
   - Preference storage (language, notifications)

3. **Rate Limiting & Abuse Prevention**
   - Per-user and per-IP rate limits on verification requests
   - CAPTCHA on anonymous uploads
   - Input validation on all endpoints

**User Schema**:
```typescript
interface User {
  userId: string;
  email?: string;
  phoneNumber?: string;
  preferredLanguage: 'hi' | 'en' | 'both';
  role: 'citizen' | 'journalist' | 'moderator' | 'admin';
  verificationHistory: VerificationRecord[];
  createdAt: Date;
  lastActiveAt: Date;
}
```

### 3.10 Reporting & Audit Service

**Purpose**: Structured, traceable records of every verification and security event.

**Components**:

1. **Verification Records (PostgreSQL)**
   - Every analysis stored with full result set
   - Includes trust score, verdict, model breakdown, and evidence references

2. **Audit Logs**
   - Verification and security events logged immutably
   - Covers uploads, analysis runs, threat lookups, admin actions
   - Timestamped with user ID, media ID, and action performed

3. **I4C / 1930 Reporting Integration**
   - Citizen reporting of confirmed deepfakes/fraud to I4C
   - Works alongside existing cyber-fraud support ecosystems
   - Exports verified evidence reports for official reporting

## 4. AI Workflow & Data Flow

### 4.1 Complete Verification Flow

```
User Upload (Image/Video/Audio/Screenshot/Link)
         ↓
┌────────────────────────────────────────────────────────────┐
│ 1. UPLOAD & INTAKE                                         │
│    - Accept file or link                                  │
│    - Validate type, size, integrity                        │
│    - Scan with VirusTotal (files/URLs)                    │
│    - Store evidence in AWS S3                              │
│    - Enqueue async verification job                       │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ 2. PREPROCESSING                                           │
│    Image  → face detect/crop/align                         │
│    Video  → keyframes + face tracks + audio track         │
│    Audio  → WAV + mel-spectrogram                          │
│    Screen → EasyOCR text extraction                        │
│    Link   → URL validation                                 │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ 3. MODAL ANALYSIS (parallel, modular AI services)          │
│    - Image: EfficientNet + XceptionNet + Gemini Vision     │
│    - Video: TimeSformer + Video Swin + Gemini Vision       │
│    - Audio: Wav2Vec2 + Whisper + Spectrogram Analysis      │
│    - Text:  EasyOCR + NLP/Scam Classifier                  │
│    - Link:  VirusTotal + Safe Browsing + PhishTank + Repo  │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ 4. RISK ENGINE (Multimodal Reasoning)                      │
│    - Normalize signals to 0–1 risk                        │
│    - Weighted fusion across available signals             │
│    - Compute Unified Trust Score (0–100)                  │
│    - Map to verdict: HIGH_TRUST / UNCERTAIN / LOW_TRUST    │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ 5. EXPLAINABLE REASONING (Gemini 2.5)                     │
│    - Generate evidence-based explanation                  │
│    - Cite influential signals (faces, frames, audio, URL) │
│    - Produce Evidence Report and Recommended Action       │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ 6. RESPONSE GENERATION                                     │
│    - Hindi-first, bilingual presentation                  │
│    - Trust Score visualization (gauge)                    │
│    - Evidence report with highlighted artifacts           │
│    - Recommended action (verify / report / share)         │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ 7. PERSISTENCE & INTEGRATION                              │
│    - Save verification record to PostgreSQL               │
│    - Cache threat intelligence results                    │
│    - Append audit log entries                             │
│    - Optional I4C/1930 reporting (user-initiated)         │
└────────────────────────────────────────────────────────────┘
         ↓
    User reviews Trust Score + Evidence Report
```

### 4.2 Trust Score Computation Flow

```
Raw Model Signals
     ↓
┌─────────────────────────────────────────┐
│ SIGNAL NORMALIZATION                    │
│ - Image: manipulation score (0-1)       │
│ - Video: authenticity score (0-1)       │
│ - Audio: voice clone score (0-1)        │
│ - Text:  scam likelihood (0-1)          │
│ - Link:  threat score (0-1)             │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│ WEIGHTED FUSION (Risk Engine)           │
│ image 0.30 + video 0.25 + audio 0.20    │
│ + ocr_nlp 0.15 + threat 0.10            │
│ (re-normalized over available signals)  │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│ TRUST SCORE (0–100)                     │
│ score = (1 - weighted_risk) × 100       │
│ ≥ 80 → HIGH_TRUST                       │
│ 50–79 → UNCERTAIN                       │
│ < 50 → LOW_TRUST                        │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│ EXPLAINABLE VERDICT (Gemini 2.5)        │
│ - Evidence report with cited artifacts  │
│ - Recommended action per verdict        │
└─────────────────────────────────────────┘
```

## 5. Database Design

### 5.1 PostgreSQL Schema

**Verification Records Table**:
```sql
CREATE TABLE verification_records (
    record_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    media_id VARCHAR(50) UNIQUE NOT NULL,
    media_type VARCHAR(20) NOT NULL,        -- 'image' | 'video' | 'audio' | 'link' | 'screenshot'
    trust_score INT NOT NULL,               -- 0-100
    verdict VARCHAR(20) NOT NULL,           -- 'HIGH_TRUST' | 'UNCERTAIN' | 'LOW_TRUST'
    recommended_action TEXT,
    model_breakdown JSONB NOT NULL,         -- per-model scores
    evidence_report JSONB NOT NULL,         -- artifacts, citations, explanation
    analysis_duration_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_media_type (media_type),
    INDEX idx_verdict (verdict),
    INDEX idx_created (created_at)
);

-- Example model_breakdown JSONB:
{
  "image": { "efficientnet": 0.82, "xceptionnet": 0.79, "gemini_vision": 0.88 },
  "video": { "timesformer": 0.74, "swin_transformer": 0.71, "gemini_vision": 0.77 },
  "audio": { "wav2vec2": 0.65, "spectrogram": 0.61, "whisper": 0.58 },
  "ocr_nlp": { "scam_likelihood": 0.90 },
  "threat": { "virus_total": 0.95, "safe_browsing": 0.92, "phishtank": 0.88 }
}
```

**Users Table**:
```sql
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(200) UNIQUE,
    phone_number VARCHAR(15) UNIQUE,
    preferred_language VARCHAR(10) DEFAULT 'hi',
    role VARCHAR(20) DEFAULT 'citizen',     -- 'citizen' | 'journalist' | 'moderator' | 'admin'
    is_anonymous BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_phone (phone_number),
    INDEX idx_role (role)
);
```

**Threat Intelligence Cache Table**:
```sql
CREATE TABLE threat_intel_cache (
    id BIGSERIAL PRIMARY KEY,
    target VARCHAR(500) UNIQUE NOT NULL,     -- URL, domain, or file hash
    target_type VARCHAR(20) NOT NULL,        -- 'url' | 'domain' | 'file_hash'
    threat_score DECIMAL(3, 2),
    vendor_verdicts JSONB,
    sources JSONB,                           -- virus_total, safe_browsing, phishtank, domain_reputation
    last_checked_at TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,           -- TTL for cache invalidation
    INDEX idx_target (target),
    INDEX idx_expires (expires_at)
);
```

**Audit Logs Table**:
```sql
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    media_id VARCHAR(50),
    event_type VARCHAR(50) NOT NULL,         -- 'upload' | 'analysis_start' | 'analysis_complete' |
                                             -- 'threat_lookup' | 'report_submitted' | 'admin_action'
    action VARCHAR(200),
    ip_address INET,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
);
```

### 5.2 Evidence Storage (AWS S3)

**Bucket Layout**:
```
s3://satya-kavach-evidence/
  uploads/{mediaId}/{original-file}
  artifacts/{mediaId}/faces/*.jpg
  artifacts/{mediaId}/frames/*.jpg
  artifacts/{mediaId}/spectrograms/*.png
  artifacts/{mediaId}/ocr-boxes/*.json
  reports/{mediaId}/evidence-report.json
```

**Object Policies**:
- Server-side encryption (SSE-KMS)
- Lifecycle rule: automatic deletion after 90 days unless user consented to longer retention
- Signed URLs only for user-facing access
- Bucket policy restricts public access; access via app role only

## 6. Scalability Design

### 6.1 Horizontal Scaling Strategy

**Stateless Services**:
- FastAPI services are stateless; verification state lives in PostgreSQL
- Analysis jobs processed asynchronously (queue + worker pool)
- Each AI model runs as an isolated, modular service — can scale independently

**Compute**:
- AWS EC2 auto-scaling groups for FastAPI and worker nodes
- Nginx as reverse proxy/load balancer
- Docker containers for consistent deployment and horizontal replication

**Async Processing**:
- Upload returns immediately with `mediaId` and job status
- Workers pull jobs, run preprocessing + model analysis
- Users poll status or receive completion via the PWA/notification

**Auto-Scaling Configuration**:
```yaml
EC2 Auto Scaling:
  - Min instances: 2 (multi-AZ)
  - Max instances: 20 during peak misinformation events
  - Scale-out: CPU > 70% for 5 minutes
  - Scale-in: CPU < 30% for 15 minutes

Worker Pool:
  - Image analysis workers: 3-10 instances
  - Video analysis workers: 3-8 instances (GPU-backed)
  - Audio analysis workers: 2-5 instances

Nginx:
  - Worker processes: auto (CPU cores)
  - Keepalive: 65s
  - Rate limit: 10 req/sec per IP for upload endpoints
```

### 6.2 Caching Strategy

**Layer 1: Client-Side Cache**
- PWA: Previous verification results (offline view)
- Web: LocalStorage for recent reports

**Layer 2: Threat Intelligence Cache (PostgreSQL)**
- URL/domain reputation results with TTL (24 hours)
- Avoids redundant external API calls to VirusTotal/Safe Browsing/PhishTank

**Layer 3: Model Result Cache**
- Same file hash (SHA-256) → cached verification result
- Deduplicates repeated uploads of the same deepfake

**Cache Invalidation**:
- Threat intel TTL expiration
- New vendor verdicts invalidate stale entries
- Media hash collisions resolve to latest analysis

### 6.3 Load Distribution

- Nginx reverse proxy → FastAPI upstreams
- Worker queues for asynchronous model inference
- S3 + CloudFront for static assets and report delivery
- Multi-AZ deployment for high availability

## 7. Security Architecture

### 7.1 Authentication & Authorization

**User Authentication**:
- JWT access tokens (short expiry) + refresh tokens
- Email/phone OTP or passwordless magic-link options
- Anonymous verification allowed (privacy-friendly) with rate limits

**Role-Based Access Control (RBAC)**:
- `citizen`: verify media, view own history
- `journalist`: verify media, batch reporting
- `moderator`: review flagged reports, manage threat intel
- `admin`: full access, audit review, model configuration

**Service-to-Service**:
- IAM roles for EC2/workers with least-privilege permissions
- API keys for external services (VirusTotal, PhishTank, Google Safe Browsing)
- Secrets stored in Secrets Manager / env-secured vault

### 7.2 Data Encryption

**In Transit**:
- TLS 1.3 (HTTPS only) via Nginx + Let's Encrypt/ACM
- HSTS enabled, HTTP redirects to HTTPS

**At Rest**:
- PostgreSQL: encrypted storage
- AWS S3: SSE-KMS server-side encryption
- Evidence artifacts encrypted with per-media data keys

**Input Validation & Secure File Handling**:
- Strict MIME-type and magic-byte validation
- File size limits, filename sanitization
- VirusTotal scan before analysis
- Metadata stripping to protect user privacy

### 7.3 Security Monitoring

**Monitoring**:
- Nginx access/error logs shipped to centralized logging
- Audit logs for verification and security events
- Failed-auth and rate-limit abuse alerts

**Abuse Prevention**:
- Rate limiting on upload endpoints
- CAPTCHA for anonymous submissions
- Deepfake-report submission limits per user

**Audit Logging**:
- All verification and security events logged immutably
- Admin actions logged separately
- Log retention: 90 days

## 8. Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### 8.1 Intake & Upload Properties

Property 1: Media Acceptance Completeness
*For any* supported media type (image, video, audio, screenshot, link) uploaded through any channel (web, PWA, voice, message), the system should validate, store, and enqueue it for analysis.
**Validates: Multimodal verification of Image • Video • Audio in one platform**

Property 2: Invalid File Rejection
*For any* upload that fails validation (wrong type, corrupted payload, oversized file), the system should reject it with a clear error and not proceed to analysis.
**Validates: Input Validation & Secure File Handling**

Property 3: Malware Pre-Scan
*For any* file or link submitted for verification, the system should run a VirusTotal security scan before AI analysis and block known malicious payloads.
**Validates: VirusTotal integration for URL/domain/file reputation**

Property 4: Upload Persistence
*For any* accepted upload, the system should persist the original media as encrypted evidence in AWS S3 with a unique media ID.
**Validates: AWS S3 secure evidence/media storage**

### 8.2 Image Detection Properties

Property 5: Face Manipulation Detection
*For any* image containing a face, the system should produce a manipulation score using the image deepfake ensemble (EfficientNet, XceptionNet, Gemini Vision).
**Validates: Deepfake Face Detection feature**

Property 6: Fake/Real Classification
*For any* image analysis, the system should output a binary Fake/Real classification derived from the manipulation score threshold.
**Validates: Image Deepfake Detection output — Manipulation Score, Fake/Real Classification**

### 8.3 Video Detection Properties

Property 7: Frame-Level Detection
*For any* video analysis, the system should evaluate temporal consistency across extracted frames and return frame-level detections.
**Validates: Video Deepfake Detection output — Frame-level Detection**

Property 8: Video Authenticity Score
*For any* video analysis, the system should combine temporal (TimeSformer, Video Swin Transformer) and spatial (Gemini Vision) signals into a single Video Authenticity Score.
**Validates: Video Authenticity Score output**

### 8.4 Audio Detection Properties

Property 9: Voice Clone Detection
*For any* audio analysis, the system should assess voice authenticity using Wav2Vec2 embeddings, spectrogram artifacts, and Whisper audio signals.
**Validates: AI Voice Clone Detection feature**

Property 10: Audio Authenticity Score
*For any* audio analysis, the system should produce an Audio Authenticity Score combining clone, spectrogram, and transcription signals.
**Validates: Audio Authenticity Score output**

### 8.5 Text & Scam Properties

Property 11: Screenshot Text Extraction
*For any* screenshot or image containing text, the system should extract embedded text via EasyOCR with bounding-box evidence.
**Validates: EasyOCR screenshot/image text extraction**

Property 12: Scam Intent Classification
*For any* extracted text or transcription, the system should classify message intent and produce a scam-likelihood score.
**Validates: NLP / Scam Classifier message & intent analysis**

### 8.6 Threat Intelligence Properties

Property 13: Link Threat Evaluation
*For any* link submitted for verification, the system should evaluate it against VirusTotal, Google Safe Browsing, and PhishTank, and return a threat score.
**Validates: Threat Intelligence integration (VirusTotal, Safe Browsing, PhishTank, Domain Reputation)**

Property 14: Threat Cache Freshness
*For any* threat-intelligence lookup, the system should consult the cache first and refresh expired entries within the TTL window.
**Validates: Threat Intelligence Cache**

### 8.7 Risk Engine Properties

Property 15: Multimodal Signal Fusion
*For any* analysis with available signals, the Risk Engine should normalize and fuse all signals (image, video, audio, OCR/NLP, threat) into one Unified Trust Score.
**Validates: Unified Trust Score feature**

Property 16: Trust Score Range
*For any* computed trust score, the value should be an integer in the range 0–100 inclusive.
**Validates: Unified Trust Score output**

Property 17: Verdict Mapping Consistency
*For any* trust score, the verdict mapping should be consistent: ≥80 → HIGH_TRUST, 50–79 → UNCERTAIN, <50 → LOW_TRUST.
**Validates: Final Verdict output**

### 8.8 Explainability Properties

Property 18: Evidence-Backed Explanation
*For any* verdict produced, the system should provide an evidence report explaining the decision, citing influential signals and artifacts.
**Validates: Explainable AI requirement — "Users need evidence-backed explanations, not just a label"**

Property 19: Recommended Action Presence
*For any* final verdict, the system should provide a recommended action appropriate to the trust level (verify / report / share).
**Validates: Action-oriented requirement — "Clear trust score and verification recommendation"**

Property 20: Model Breakdown Transparency
*For any* verification record, the system should expose the per-model score breakdown so users and moderators can audit the computation.
**Validates: Explainable results requirement**

### 8.9 Data & Persistence Properties

Property 21: Verification Record Persistence
*For any* completed analysis, the system should persist the full verification record (score, verdict, breakdown, evidence) to PostgreSQL.
**Validates: PostgreSQL — users, reports, scores, analysis history**

Property 22: Evidence Retention Limit
*For any* evidence artifact stored in S3, it should be automatically deleted after 90 days unless the user has explicitly consented to longer retention.
**Validates: Secure evidence handling**

Property 23: Audit Log Completeness
*For any* verification or security event (upload, analysis, threat lookup, admin action), the system should create an audit log entry with timestamp, user, and action.
**Validates: Audit Logs — verification & security events**

Property 24: Analysis Idempotency
*For any* media re-uploaded with the same SHA-256 hash, the system should return the cached verification result instead of re-running full analysis.
**Validates: Scalable, stateless API design**

### 8.10 Security & Privacy Properties

Property 25: Authenticated Access Control
*For any* request to user data or verification history, the system should authenticate the JWT and enforce role-based permissions.
**Validates: JWT Authentication**

Property 26: Secure File Handling
*For any* file accepted by the system, it should be validated, sanitized, and scanned before storage and analysis.
**Validates: Secure File Handling**

Property 27: Deepfake Report Integration
*For any* user-initiated report of a confirmed deepfake, the system should support handoff to the I4C / 1930 reporting ecosystem with an exported evidence report.
**Validates: I4C / 1930 Ecosystem — citizen reporting & cyber-fraud support**

### 8.11 Asynchronous Processing Properties

Property 28: Async Job Progress Tracking
*For any* submitted verification job, the system should maintain and expose a job status (queued → preprocessing → analyzing → scoring → complete) until completion.
**Validates: Async Processing, Stateless APIs**

Property 29: Modular Failure Isolation
*For any* single AI service failure during analysis, the system should continue processing with remaining signals and mark the failed signal as unavailable.
**Validates: Modular AI Services, graceful degradation**

## 9. Error Handling

### 9.1 Error Categories

**1. User Input Errors**
- Unsupported file type or corrupted file
- Oversized upload
- Invalid/malicious URL
- Response: Clear rejection message with supported formats

**2. Model/Service Errors**
- Image/Video/Audio model unavailability
- Gemini reasoning timeout
- Whisper/Wav2Vec2 failure
- Response: Continue with remaining signals, mark signal unavailable, flag uncertainty

**3. Integration Errors**
- VirusTotal / Safe Browsing / PhishTank API failures
- Threat intelligence rate limits
- Response: Fall back to cached threat results; omit threat signal if unavailable

**4. Storage Errors**
- S3 upload failure
- PostgreSQL connection failure
- Response: Retry with exponential backoff, fail the job gracefully with a retryable status

### 9.2 Error Handling Strategies

**Retry Logic**:
```python
import time

def with_retry(operation, max_retries=3, base_delay=1.0):
    """Exponential backoff retry for transient failures."""
    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except TransientError:
            if attempt == max_retries:
                raise
            time.sleep(base_delay * (2 ** (attempt - 1)))
```

**Graceful Degradation**:
```python
def analyze_media(job: AnalysisJob) -> TrustResult:
    signals = {}
    try:
        signals['image'] = image_detector.analyze(job.face_tiles, job.ctx)
    except ModelError as e:
        logger.warning(f"Image detector unavailable: {e}")
        signals['image'] = None

    try:
        signals['video'] = video_detector.analyze(job.frames, job.tracks)
    except ModelError as e:
        logger.warning(f"Video detector unavailable: {e}")
        signals['video'] = None

    # Risk Engine re-normalizes weights over available signals only
    return risk_engine.compute_trust_score(signals)
```

**Circuit Breaker**:
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failures = 0
        self.threshold = failure_threshold
        self.state = 'closed'          # 'closed' | 'open' | 'half-open'
        self.last_failure = 0

    def call(self, operation):
        if self.state == 'open':
            if time.time() - self.last_failure > self.reset_timeout:
                self.state = 'half-open'
            else:
                raise ServiceUnavailableError("Threat intel circuit open")

        try:
            result = operation()
            self.failures = 0
            self.state = 'closed'
            return result
        except Exception:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = 'open'
            raise
```

### 9.3 User-Facing Error Messages

**Error Message Principles**:
- Simple, plain language (Hindi-first)
- Actionable guidance (what user should do next)
- No technical jargon
- Empathetic tone

**Examples**:
```typescript
const errorMessages = {
  unsupported_file: {
    hi: "कृपया सही फ़ाइल प्रकार अपलोड करें: इमेज, वीडियो, या ऑडियो।",
    en: "Please upload a supported file type: image, video, or audio."
  },
  file_too_large: {
    hi: "फ़ाइल बहुत बड़ी है। कृपया छोटी फ़ाइल अपलोड करें।",
    en: "The file is too large. Please upload a smaller file."
  },
  analysis_incomplete: {
    hi: "कुछ जाँच पूरी नहीं हो सकीं। परिणाम सीमित हो सकता है।",
    en: "Some checks could not be completed. The result may be limited."
  },
  system_busy: {
    hi: "अभी बहुत व्यस्त हैं। कृपया कुछ क्षण बाद पुनः प्रयास करें।",
    en: "We're experiencing high traffic. Please try again in a moment."
  }
};
```

## 10. Testing Strategy

### 10.1 Dual Testing Approach

The system requires both unit testing and property-based testing for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs
- Together they provide comprehensive coverage: unit tests catch concrete bugs, property tests verify general correctness

### 10.2 Unit Testing

**Scope**:
- Specific detection scenarios (known deepfake samples from DFDC, FaceForensics++, ASVspoof)
- Edge cases (empty files, boundary sizes, corrupt media)
- Error conditions (model failures, threat-intel timeouts)
- Integration points between components

**Example Unit Tests**:
```python
def test_low_trust_image_verdict():
    # FaceForensics++ manipulated sample
    result = verify_image(load_sample("ffpp_manipulated_001.jpg"))
    assert result.trust_score < 50
    assert result.verdict == "LOW_TRUST"

def test_high_trust_authentic_audio():
    result = verify_audio(load_sample("asvspoof_bonafide_001.wav"))
    assert result.trust_score >= 80
    assert result.verdict == "HIGH_TRUST"

def test_reject_invalid_file():
    with pytest.raises(ValidationError):
        verify_upload(b"not-a-real-file", "image/jpeg")

def test_graceful_degradation_on_model_failure():
    # Stub image detector to raise; other signals must still produce a verdict
    signals = run_with_failed_image_signal()
    assert signals["image"] is None
    assert signals["audio"] is not None
```

**Testing Tools**:
- **Python**: pytest, unittest
- **Frontend**: Jest, React Testing Library
- **Mocking**: AI service stubs, threat-intel API mocks
- **Coverage Target**: 80% code coverage

### 10.3 Property-Based Testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `Feature: satya-kavach, Property {number}: {property_text}`

**Property Testing Library**:
- **Python**: Hypothesis

**Example Property Tests**:
```python
from hypothesis import given, strategies as st

# Feature: satya-kavach, Property 16: Trust Score Range
@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
def test_trust_score_always_in_range(signal_risk):
    signals = {"image": signal_risk}
    result = risk_engine.compute_trust_score(signals)
    assert 0 <= result.trust_score <= 100
    assert isinstance(result.trust_score, int)

# Feature: satya-kavach, Property 17: Verdict Mapping Consistency
@given(st.integers(min_value=0, max_value=100))
def test_verdict_mapping_is_consistent(score):
    verdict = risk_engine.map_verdict(score)
    if score >= 80:
        assert verdict == "HIGH_TRUST"
    elif score >= 50:
        assert verdict == "UNCERTAIN"
    else:
        assert verdict == "LOW_TRUST"

# Feature: satya-kavach, Property 24: Analysis Idempotency
@given(st.binary(min_size=1, max_size=1024))
def test_same_hash_returns_cached_result(media_bytes):
    media_id_1 = ingest(media_bytes)
    media_id_2 = ingest(media_bytes)  # identical content
    assert cached_result(media_id_2).record_id == cached_result(media_id_1).record_id
```

### 10.4 Integration Testing

**Scope**:
- End-to-end upload → preprocessing → analysis → trust score → report flow
- Each AI model integration (EfficientNet, TimeSformer, Wav2Vec2, Whisper, EasyOCR)
- Threat intelligence integrations (VirusTotal, Safe Browsing, PhishTank)
- Database operations (PostgreSQL, S3)

**Tools**:
- Docker Compose for local service orchestration
- LocalStack / MinIO for S3 mocking
- Postman/Newman for API testing
- Cypress for web/PWA UI testing

### 10.5 Load Testing

**Scope**:
- Concurrent verification requests (100, 500, 1000)
- Response time under load for sync endpoints
- Async worker throughput for video/audio analysis
- Database performance under concurrent writes

**Tools**:
- Apache JMeter
- Artillery.io
- k6

**Test Scenarios**:
- Steady state: 100 concurrent uploads for 1 hour
- Spike: 0 to 500 uploads in 1 minute (misinformation event)
- Gradual ramp: 0 to 1000 uploads over 30 minutes

### 10.6 Security Testing

**Scope**:
- Malware upload handling (VirusTotal path)
- Malicious URL detection
- JWT/token validation and role enforcement
- File upload abuse (type confusion, path traversal)

**Tools**:
- OWASP ZAP
- Burp Suite
- Manual security review
- Vendor API key rotation checks

### 10.7 Continuous Testing

**CI/CD Pipeline**:
```yaml
stages:
  - lint
  - unit-test
  - property-test
  - integration-test
  - security-scan
  - deploy-staging
  - smoke-test
  - deploy-production

unit-test:
  script:
    - pytest tests/unit
  coverage: 80%

property-test:
  script:
    - pytest tests/property
  allow_failure: false  # Property tests must pass

integration-test:
  script:
    - docker-compose up -d
    - pytest tests/integration
```

## 11. DevOps & CI/CD Strategy

### 11.1 Containerization

**Dockerfile for FastAPI Service**:
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose for Local Development**:
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api

  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/satya
      - S3_ENDPOINT=http://minio:9000
    depends_on:
      - postgres
      - minio

  worker:
    build: ./backend
    command: celery -A app.workers worker
    depends_on:
      - api

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: satya
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
```

### 11.2 Deployment Architecture

**Production (AWS EC2 + Docker)**:
- Nginx reverse proxy → FastAPI containers (multiple replicas)
- Celery workers for async model analysis
- AWS S3 for evidence storage
- PostgreSQL (managed or EC2) for relational data
- Docker images built in CI and deployed to EC2 instances

**Environment Separation**:
- `staging`: Pre-production, real model samples, test threat-intel keys
- `production`: Full model stack, real threat-intel API keys, I4C/1930 integration enabled

### 11.3 Deployment Pipeline

**GitHub Actions Workflow**:
```yaml
name: Deploy SatyaKavach

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest tests/unit
      - run: pytest tests/property
      - run: pytest tests/integration

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Snyk Security Scan
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  deploy-staging:
    needs: [test, security-scan]
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and Push Docker Image
        run: |
          docker build -t satya-backend:staging ./backend
          docker push ${{ secrets.REGISTRY }}/satya-backend:staging
      - name: Deploy to Staging EC2
        run: |
          ssh ec2-user@${{ secrets.STAGING_HOST }} \
            "docker compose pull && docker compose up -d"

  deploy-production:
    needs: [test, security-scan]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      - name: Build and Push Docker Image
        run: |
          docker build -t satya-backend:prod ./backend
          docker push ${{ secrets.REGISTRY }}/satya-backend:prod
      - name: Deploy to Production EC2
        run: |
          ssh ec2-user@${{ secrets.PROD_HOST }} \
            "docker compose pull && docker compose up -d"
      - name: Run Smoke Tests
        run: pytest tests/smoke
```

### 11.4 Monitoring & Observability

**Key Metrics**:
- Verification throughput and queue depth
- Per-model inference latency and failure rate
- Trust Score distribution (HIGH_TRUST / UNCERTAIN / LOW_TRUST)
- Threat-intel API quota usage and error rate
- Upload volume spikes (misinformation event detection)

**Alerting**:
```yaml
alarms:
  - name: HighWorkerQueueDepth
    metric: QueueDepth
    threshold: 500
    period: 300
    actions: [notify_ops]

  - name: HighModelFailureRate
    metric: ModelFailureRate
    threshold: 0.05
    period: 300
    actions: [notify_ops]

  - name: ThreatIntelQuotaExhaustion
    metric: ThreatIntelApiErrors
    threshold: 10
    period: 600
    actions: [notify_ops]
```

**Logging**:
- Structured JSON logs for all services
- Audit logs for verification/security events
- Model inference traces (media ID → models → scores) for debugging explainability

## 12. Future Extensibility

### 12.1 Expanding Detection Capabilities

**Planned Enhancements**:
1. **More Image Models**: Add Face X-ray, Capsule-Net, and CNN artifacts detectors to the ensemble
2. **Real-Time Video Verification**: Streaming analysis for live video and video calls
3. **Synthetic Media Attribution**: Attribution fingerprinting to identify the generating model
4. **GAN Image Detection**: Dedicated detectors for GAN/diffusion-generated images
5. **Deepfake Benchmarks**: Continuous evaluation against DeepFakeBench and new datasets

**Process**:
- Register new model in the model registry (modular AI services)
- Add dataset configuration for training/evaluation
- Validate against DFDC, FaceForensics++, Celeb-DF v2, ASVspoof 2019, FakeAVCeleb, WaveFake
- Deploy as isolated service; Risk Engine re-weights signals

### 12.2 New Media Types & Sources

**Planned Additions**:
1. **PDF/Document Forensics**: Metadata and digital-signature analysis for official documents
2. **Deepfake Video in Messaging Apps**: Forwarding/verification within messaging ecosystems
3. **Broadcast Media Verification**: Verification for TV/radio clips
4. **Multimodal Batch Analysis**: Verify multiple media items in a single report

### 12.3 Ecosystem & Government Integration

**Future Integration Points**:

1. **I4C / 1930 Deeper Integration**:
   - One-click reporting of confirmed deepfakes to the cyber-fraud ecosystem
   - Structured evidence package (trust score + report) accepted by authorities
   - Two-way status updates on submitted reports

2. **Fact-Checking Organization APIs**:
   - Journalist/educator API access for bulk verification
   - Claim-to-media association and evidence export
   - Integration with media literacy campaigns

3. **MeitY / Digital India Alignment**:
   - Support for responsible AI adoption frameworks
   - Media authenticity verification standards
   - Explainable AI tooling for public trust

### 12.4 Enhanced Explainability

**Planned Enhancements**:
1. **Per-Face Heatmaps**: Visualize manipulation regions (face blending, artifacts) on the media
2. **Spectral Visualization**: Interactive spectrogram views for audio findings
3. **Model Confidence Drill-Down**: Expandable per-model scores with plain-language meaning
4. **Comparative History**: Show whether similar deepfakes have been verified previously
5. **Multi-Language Evidence Reports**: Localized reports beyond Hindi/English (Tamil, Telugu, Bengali)

### 12.5 Analytics & Insights

**Future Analytics Features**:
1. **Deepfake Trend Monitoring**: Track emerging manipulation techniques and hotspots
2. **Misinformation Event Alerts**: Detect upload spikes correlated with viral campaigns
3. **Impact Measurement**: Measure user adoption, reports filed, and awareness outcomes
4. **A/B Testing Framework**: Test different trust-score presentations and report layouts

### 12.6 Scalability Roadmap

**Phase 1 (Current)**: State-level launch, Hindi-first
- Single-region AWS EC2 + Docker + Nginx
- Core multimodal pipeline (image, video, audio)
- VirusTotal + Safe Browsing + PhishTank integration

**Phase 2 (3-6 months)**: Nationwide scale
- Auto-scaling EC2 fleets + worker pool expansion
- Multi-language evidence reports
- Fact-checker and journalist API access
- Real-time video verification

**Phase 3 (6-12 months)**: Multi-region & enterprise
- Multi-region deployment and global load balancing
- I4C / 1930 bidirectional integration
- Government/media partnerships
- Continuous model retraining against new deepfake benchmarks

## 13. Use Cases & Demo Scenarios

### 13.1 Citizen Verifies a Viral Deepfake Video

**Context**: A citizen receives a WhatsApp video of a public figure saying something inflammatory. It is spreading faster than verified content.

**Flow**:
1. User uploads the video (or pastes its link) in the Hindi-first PWA.
2. Preprocessing extracts keyframes, face tracks, and the audio track.
3. Video models (TimeSformer + Video Swin Transformer + Gemini Vision) flag frame-level blending artifacts.
4. Audio models (Wav2Vec2 + Whisper) detect a synthetic voice.
5. Risk Engine fuses signals → **Trust Score 12/100 → LOW_TRUST**.

**Outcome**: User sees the evidence report (highlighted manipulated frames, low voice-authenticity score, cited artifacts) and the recommended action: *"Do not share. Report to I4C/1930."* One-tap report exports the evidence package.

### 13.2 Journalist Fact-Checks a Screenshot with a Link

**Context**: A journalist receives a screenshot of a "government subsidy" message containing a suspicious link, minutes before publication.

**Flow**:
1. User uploads the screenshot.
2. EasyOCR extracts the embedded text (Hindi + English).
3. NLP / Scam Classifier detects financial-ask and urgency intent.
4. Threat Intelligence checks the link against VirusTotal, Google Safe Browsing, PhishTank, and Domain Reputation.
5. Risk Engine fuses OCR/NLP + threat signals → **Trust Score 08/100 → LOW_TRUST** with the malicious URL cited.

**Outcome**: The journalist avoids propagating a phishing link, and the threat-intel cache blocks future checks of the same URL.

### 13.3 User Verifies a Suspicious Voice Clip (AI Voice Clone)

**Context**: A user receives an audio clip that sounds like a family member urgently requesting money.

**Flow**:
1. User uploads the audio.
2. Wav2Vec2 analyzes the voice embedding; Whisper transcribes; spectrogram analysis checks for synthesis artifacts.
3. Voice Clone Detection flags a synthetic voice; NLP classifier detects urgency + financial ask.
4. Risk Engine → **Trust Score 18/100 → LOW_TRUST**.

**Outcome**: The user sees the audio authenticity score, the transcript evidence, and the recommended action to verify directly and report the fraud. This directly addresses AI voice-clone fraud targeting citizens.

### 13.4 Educator Verifies Authentic Media for a Lesson

**Context**: An educator checks an authentic government public-service image before using it in class.

**Flow**:
1. User uploads the image.
2. Image ensemble (EfficientNet + XceptionNet + Gemini Vision) finds no manipulation artifacts.
3. Risk Engine → **Trust Score 94/100 → HIGH_TRUST**.

**Outcome**: The educator sees the per-model breakdown and evidence, confirming authenticity while modeling good verification habits — reinforcing media literacy and explainable-AI trust.

### 13.5 Deepfake Report Escalated to I4C / 1930 Ecosystem

**Context**: A confirmed deepfake of a public figure is circulating at scale; a citizen/moderator reports it.

**Flow**:
1. Confirmed LOW_TRUST verification record is exported as a structured evidence package.
2. Report is handed to the I4C / 1930 cyber-fraud ecosystem for official action.
3. Audit log records the submission; user receives a confirmation and tracking reference.

**Outcome**: The platform works *alongside existing systems*, turning AI verification into actionable cyber-fraud reporting.

## 14. Hackathon MVP Scope & Delivery Plan

### 14.1 MVP Scope (In)

- **Image verification**: EfficientNet + XceptionNet ensemble with Gemini Vision corroboration → Manipulation Score + Fake/Real
- **Video verification**: TimeSformer + Video Swin Transformer → Frame-level detection + Video Authenticity Score
- **Audio verification**: Wav2Vec2 + Whisper + spectrogram analysis → Voice Clone Detection + Audio Authenticity Score
- **Text verification**: EasyOCR + NLP / Scam Classifier → scam likelihood
- **Link verification**: VirusTotal + Google Safe Browsing + PhishTank + Domain Reputation → threat score
- **Risk Engine**: Multimodal fusion → Unified Trust Score (0–100), verdict, recommended action
- **Explainability**: Gemini 2.5 evidence report with cited artifacts
- **Frontend**: React + TypeScript + Tailwind PWA, Hindi-first UI, upload/link intake, trust-score gauge, evidence report view
- **Persistence**: PostgreSQL verification records + audit logs; S3 evidence storage
- **Security**: JWT auth, input validation, secure file handling, rate limiting

### 14.2 MVP Scope (Out — Post-Hackathon)

- I4C/1930 two-way status tracking (one-way report stub in MVP)
- Real-time / streaming video verification
- Additional Indian languages beyond Hindi/English
- Public API for journalist bulk verification

### 14.3 Delivery Milestones (Hackathon Timeline)

| Milestone | Scope | Deliverable |
|-----------|-------|-------------|
| M1 — Foundations (0–6h) | FastAPI + React scaffold, PostgreSQL + S3 (MinIO), Docker Compose | Running skeleton, upload endpoint |
| M2 — Preprocessing (6–10h) | Frame extraction, face crop/align, audio extraction, EasyOCR, Whisper | Artifacts pipeline |
| M3 — Modal Detectors (10–18h) | Image ensemble, video models, audio models | Per-modal verdicts |
| M4 — Fusion & Reasoning (18–24h) | Risk Engine + Gemini explainability + threat intel | Trust Score + evidence report |
| M5 — Frontend (24–32h) | Hindi-first PWA, upload flow, results UI, auth | Usable end-to-end product |
| M6 — Hardening & Polish (32–40h) | Tests, error handling, audit logs, demo datasets | Demo-ready build |
| M7 — Demo Prep (40–48h) | Scenario walkthroughs, performance pass, pitch materials | Final demo |

### 14.4 Team Roles (Suggested)

| Role | Responsibility |
|------|----------------|
| ML Engineer | Deepfake models, preprocessing, model ensemble, risk engine |
| Backend Engineer | FastAPI, async jobs, PostgreSQL, S3, threat-intel integrations |
| Frontend Engineer | React + Tailwind PWA, Hindi-first UI, evidence visualization |
| DevOps / Security | Docker, Nginx, CI/CD, JWT, secure file handling, audit logs |
| Data / Researcher | Dataset curation (DFDC, FaceForensics++, ASVspoof, FakeAVCeleb), accuracy validation |

## 15. KPIs & Impact Metrics

### 15.1 Detection Accuracy

- **Image**: Accuracy / AUC on FaceForensics++ and Celeb-DF v2
- **Video**: Frame-level AUC on DFDC; temporal consistency score
- **Audio**: Voice-clone detection AUC on ASVspoof 2019 and WaveFake
- **Fusion**: End-to-end trust-score accuracy against known manipulated/authentic samples (DeepFakeBench)

### 15.2 User & Product Metrics

- **Time-to-verdict**: image < 10s, video < 60s, audio < 30s (async target)
- **Trust Score reliability**: low rate of FALSE_TRUST (authentic marked fake) and FALSE_FAKE (fake marked real)
- **Explainability**: % of verdicts with a complete, cited evidence report
- **Adoption**: number of verifications per day, anonymous vs logged-in usage

### 15.3 Societal Impact

- **Deepfakes flagged**: count of LOW_TRUST media identified
- **Reports escalated**: submissions to I4C / 1930 ecosystem
- **Misinformation curbed**: estimated shares prevented (X faster spread avoided)
- **Trust in digital media**: user-reported confidence in verification results

## 16. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model false positives on authentic media | Users lose trust | Ensemble + Gemini corroboration, confidence thresholds, "UNCERTAIN" zone, human review path |
| Evolving deepfake generation techniques | Detection degradation | Modular model registry, continuous retraining on new datasets (DeepFakeBench), multi-model ensemble |
| Hindi/low-literacy UI adoption | Low accessibility | Hindi-first interface, voice/screenshot upload, plain-language evidence, PWA installability |
| API/cloud cost at scale | Sustainability | Async processing, stateless services, S3 lifecycle rules, caching (SHA-256 dedup + threat-intel cache) |
| Threat-intel dependency (VirusTotal, PhishTank) | Link verification gaps | Multi-vendor fusion, graceful degradation to AI-only signals, cache to reduce rate-limit pressure |
| Privacy concerns on media upload | Low trust in the platform | Minimal data collection, encrypted S3 storage, 90-day retention, audit logs, no sharing without consent |

## 17. Roadmap (Post-Hackathon)

### 17.1 Phase A (0–3 months): MVP to Public Pilot
- Production hardening, multi-language UI (Tamil, Telugu, Bengali)
- I4C/1930 bidirectional integration
- Public API + journalist/fact-checker access
- WhatsApp bot for verification-on-the-go

### 17.2 Phase B (3–6 months): Nationwide Scale
- Multi-region deployment, auto-scaling
- Real-time video verification
- Government & media partnerships
- Media-literacy campaigns with educational institutions

### 17.3 Phase C (6–12 months): Intelligence & Ecosystem
- Deepfake trend monitoring and misinformation-event alerts
- Continuous model benchmarking against DeepFakeBench
- Synthetic-media attribution (fingerprinting generating models)
- Federated/citizen-science verification network

---

**Document Version:** 2.0  
**Last Updated:** August 2026  
**Status:** Ready for Hackathon Submission