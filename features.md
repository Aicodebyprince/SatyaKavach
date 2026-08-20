# Features Document: SatyaKavach – AI-Powered Deepfake & Manipulated Media Detection

> **Connected Documents**: [design.md](./design.md) (architecture & design) · [requirements.md](./requirements.md) (requirements & acceptance criteria) · [roadmap.md](./roadmap.md) (delivery phases)
>
> This document defines every product feature of SatyaKavach, its priority, dependencies, and how it maps to the requirements and the system architecture.

## 1. Introduction

SatyaKavach is a citizen-first, multimodal AI verification platform that detects deepfake and manipulated media across **images, videos, and audio**, and delivers a **Unified Trust Score**, an **evidence-based explanation**, and a **recommended action**.

This feature catalogue translates the product vision (see [design.md §1](./design.md)) into concrete, buildable features. Each feature links to:
- **Requirements** (FR = Functional Requirement, NFR = Non-Functional Requirement) in [requirements.md](./requirements.md)
- **Architecture components** in [design.md](./design.md)
- **Delivery phases** in [roadmap.md](./roadmap.md)

## 2. Feature Priority Matrix

| Priority | Meaning | Delivery |
|----------|---------|----------|
| **P0 — Must Have** | Core to the hackathon MVP demo | Roadmap Phase A |
| **P1 — Should Have** | Needed for a complete pilot | Roadmap Phase B |
| **P2 — Could Have** | Differentiators / post-pilot | Roadmap Phase C |
| **P3 — Won't Have Yet** | Backlog / future extensibility | Roadmap Phase C+ |

## 3. Functional Feature Catalogue

### F1: Multimodal Media Upload

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Accept images (PNG/JPEG/WebP), videos (MP4/MOV), audio (MP3/WAV/M4A), screenshots, and links for verification, from both logged-in and anonymous users.

**User Story**: *As a citizen, I want to upload any suspicious media (image, video, audio, screenshot, or link) in one place, so that I can verify it without switching between tools.*

**Acceptance Criteria**:
1. WHEN a user uploads an image, video, audio, screenshot, or link THEN the system SHALL accept it and start analysis
2. WHEN a file is not a supported type THEN the system SHALL reject it with a clear Hindi-first error message
3. WHEN a file exceeds the size limit THEN the system SHALL reject it with guidance
4. WHEN an upload succeeds THEN the system SHALL return a unique media ID and job status immediately
5. WHEN the same media is uploaded again THEN the system SHALL return the cached result (SHA-256 deduplication)

**Links**: Requirements FR-01, NFR-18 · Design §3.1, §3.2 · Roadmap Phase A

---

### F2: Deepfake Face Detection (Image)

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Detect manipulated or AI-synthesized faces in images using an ensemble of EfficientNet + XceptionNet with Gemini Vision corroboration. Outputs a **Manipulation Score** and **Fake/Real Classification**.

**User Story**: *As a social media user, I want to know if a shared photo of a person has been altered, so that I do not spread manipulated content.*

**Acceptance Criteria**:
1. WHEN an image containing a face is analyzed THEN the system SHALL produce a manipulation score (0–1)
2. WHEN the manipulation score exceeds 0.5 THEN the system SHALL classify the image as "fake"
3. WHEN the manipulation score is at or below 0.5 THEN the system SHALL classify the image as "real"
4. WHEN multiple faces exist THEN the system SHALL report a per-face manipulation score
5. WHEN model confidence is low THEN the system SHALL mark the result as "uncertain" for human review

**Links**: Requirements FR-02 · Design §3.3 · Roadmap Phase A

---

### F3: Video Deepfake Detection

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Detect temporal and frame-level manipulation in videos using TimeSformer + Video Swin Transformer with Gemini Vision frame verification. Outputs **Frame-level Detection** and a **Video Authenticity Score**.

**User Story**: *As a journalist, I want to verify whether a video is genuine before reporting on it, so that I maintain editorial integrity.*

**Acceptance Criteria**:
1. WHEN a video is analyzed THEN the system SHALL extract keyframes and face tracks for analysis
2. WHEN temporal inconsistencies are detected THEN the system SHALL flag specific frames
3. WHEN a video contains an audio track THEN the system SHALL analyze it with the audio pipeline
4. WHEN a video passes all checks THEN the system SHALL return a high Video Authenticity Score
5. WHEN manipulation is detected in any frames THEN the system SHALL list those frame locations as evidence

**Links**: Requirements FR-03 · Design §3.4 · Roadmap Phase A

---

### F4: AI Voice Clone Detection

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Detect synthetic or cloned voices using Wav2Vec2 embeddings, Whisper transcription signals, and audio spectrogram artifact analysis. Outputs **Voice Clone Detection** and an **Audio Authenticity Score**.

**User Story**: *As a citizen, I want to verify whether a voice message is really from the person it claims to be, so that I am not deceived by voice-cloning fraud.*

**Acceptance Criteria**:
1. WHEN audio is analyzed THEN the system SHALL produce a voice-clone detection result
2. WHEN audio is analyzed THEN the system SHALL produce an Audio Authenticity Score (0–1)
3. WHEN speech is present THEN the system SHALL transcribe it (Hindi/English) as evidence
4. WHEN a voice clone is detected THEN the system SHALL flag the audio as HIGH-RISK
5. WHEN audio quality is poor THEN the system SHALL note reduced confidence in the report

**Links**: Requirements FR-04 · Design §3.5 · Roadmap Phase A

---

### F5: Media Forensics Engine

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Analyze images, videos, and audio for signs of tampering, editing, re-compression, splicing, and manipulation — acting as the cross-modal forensic backbone feeding the Risk Engine.

**User Story**: *As a fact-checker, I want forensic signals (metadata, artifacts, inconsistencies) so that I can understand how media may have been manipulated.*

**Acceptance Criteria**:
1. WHEN media is analyzed THEN the system SHALL detect editing artifacts (blending, splicing, compression traces)
2. WHEN media contains tampering evidence THEN the system SHALL list the specific artifacts found
3. WHEN a video has been spliced THEN the system SHALL flag scene-boundary anomalies
4. WHEN the file metadata conflicts with content THEN the system SHALL flag the inconsistency
5. WHEN no artifacts are found THEN the system SHALL report "no manipulation artifacts detected"

**Links**: Requirements FR-05 · Design §3.2, §3.3, §3.4, §3.5 · Roadmap Phase A

---

### F6: OCR Text Extraction (EasyOCR)

**Priority**: P1 · **Status**: Planned · **Roadmap**: Phase B

**Description**: Extract embedded text from screenshots and images using EasyOCR (Hindi + English) to feed the NLP / Scam Classifier and surface scam indicators.

**User Story**: *As a citizen, I want to verify a screenshot of a message, so that I can tell whether it is a scam.*

**Acceptance Criteria**:
1. WHEN a screenshot is uploaded THEN the system SHALL extract embedded text with EasyOCR
2. WHEN text contains Hindi or English THEN the system SHALL extract both
3. WHEN text is extracted THEN the system SHALL preserve bounding-box coordinates as evidence
4. WHEN no readable text exists THEN the system SHALL report that no text was found

**Links**: Requirements FR-06 · Design §3.6 · Roadmap Phase B

---

### F7: NLP / Scam Intent Classifier

**Priority**: P1 · **Status**: Planned · **Roadmap**: Phase B

**Description**: Classify the intent of extracted text / transcriptions and detect scam indicators (urgency, financial asks, impersonation, OTP fraud).

**User Story**: *As a citizen, I want to know whether a suspicious message is a scam, so that I can avoid fraud.*

**Acceptance Criteria**:
1. WHEN text or transcription is available THEN the system SHALL classify message intent
2. WHEN scam indicators (urgency, money, OTP, impersonation) are found THEN the system SHALL list them
3. WHEN scam likelihood is high THEN the system SHALL raise the overall risk contribution
4. WHEN the message is benign THEN the system SHALL report low scam likelihood

**Links**: Requirements FR-07 · Design §3.6 · Roadmap Phase B

---

### F8: Threat Intelligence (URL / Domain / File Reputation)

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Enrich link verification with VirusTotal, Google Safe Browsing, PhishTank, and Domain Reputation signals, cached to avoid redundant lookups.

**User Story**: *As a user, I want to know whether a link in a message is malicious, so that I do not click on phishing or malware URLs.*

**Acceptance Criteria**:
1. WHEN a link is submitted THEN the system SHALL query VirusTotal, Google Safe Browsing, PhishTank, and Domain Reputation
2. WHEN a link is flagged by any source THEN the system SHALL raise the threat score
3. WHEN a link was checked recently THEN the system SHALL return the cached verdict within TTL
4. WHEN external threat-intel APIs are unavailable THEN the system SHALL degrade gracefully and note the missing signal

**Links**: Requirements FR-08 · Design §3.7 · Roadmap Phase A

---

### F9: Unified Trust Score & Verdict (Risk Engine)

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Fuse all available signals (image, video, audio, OCR/NLP, threat) into a single **Trust Score (0–100)** and a verdict: **HIGH_TRUST / UNCERTAIN / LOW_TRUST**.

**User Story**: *As a citizen, I want one simple number that tells me how much I can trust a piece of media, so that I can act confidently.*

**Acceptance Criteria**:
1. WHEN at least one signal is available THEN the system SHALL compute a Unified Trust Score (0–100)
2. WHEN the score is ≥ 80 THEN the system SHALL classify the media as HIGH_TRUST
3. WHEN the score is 50–79 THEN the system SHALL classify the media as UNCERTAIN
4. WHEN the score is < 50 THEN the system SHALL classify the media as LOW_TRUST
5. WHEN a signal is unavailable THEN the system SHALL re-normalize weights over available signals only
6. WHEN the verdict is UNCERTAIN THEN the system SHALL recommend further verification

**Links**: Requirements FR-09 · Design §3.8, §4.2 · Roadmap Phase A

---

### F10: Explainable Evidence Report

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Gemini 2.5 generates a plain-language, evidence-backed explanation citing the most influential signals and artifacts (manipulated frames, spectrograms, OCR boxes, vendor verdicts).

**User Story**: *As a user, I want to see why the system made its decision, so that I can trust the verdict — not just a "fake" or "real" label.*

**Acceptance Criteria**:
1. WHEN a verdict is produced THEN the system SHALL generate an evidence report in plain language
2. WHEN artifacts influenced the verdict THEN the report SHALL cite them with visual evidence
3. WHEN a verdict is HIGH_TRUST THEN the report SHALL explain which checks passed
4. WHEN a verdict is LOW_TRUST THEN the report SHALL highlight the strongest manipulation signals
5. THE report SHALL be available in Hindi and English

**Links**: Requirements FR-10 · Design §3.8 · Roadmap Phase A

---

### F11: Recommended Action

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Provide a clear, actionable recommendation based on the verdict (verify / cross-check / do not share / report to I4C/1930).

**User Story**: *As a citizen, I want to know what to do next, so that I can act responsibly with the verified result.*

**Acceptance Criteria**:
1. WHEN the verdict is HIGH_TRUST THEN the system SHALL recommend "likely authentic — verify context before sharing"
2. WHEN the verdict is UNCERTAIN THEN the system SHALL recommend "further verification recommended"
3. WHEN the verdict is LOW_TRUST THEN the system SHALL recommend "do not share — report to I4C/1930"
4. WHEN LOW_TRUST media is detected THEN the system SHALL offer a one-tap report action

**Links**: Requirements FR-11 · Design §3.8 · Roadmap Phase A

---

### F12: I4C / 1930 Reporting & Audit

**Priority**: P1 · **Status**: Planned · **Roadmap**: Phase B

**Description**: Hand off confirmed deepfake / cyber-fraud reports to the I4C / 1930 ecosystem with an exported structured evidence package, and maintain immutable audit logs.

**User Story**: *As a citizen, I want to report a confirmed deepfake to the authorities, so that action can be taken.*

**Acceptance Criteria**:
1. WHEN a user initiates a report THEN the system SHALL export the evidence package
2. WHEN a report is submitted THEN the system SHALL record it in the audit log
3. WHEN a report is submitted THEN the system SHALL confirm submission to the user
4. WHEN a user has no account THEN the system SHALL still allow reporting anonymously

**Links**: Requirements FR-12 · Design §3.10 · Roadmap Phase B

---

### F13: Hindi-First Citizen Interface (PWA)

**Priority**: P0 · **Status**: Planned · **Roadmap**: Phase A

**Description**: Installable, mobile-first PWA built with React.js + TypeScript + Tailwind CSS, Hindi-first bilingual UI, supporting upload, voice, screenshot, message, and link intake with a clear Trust Score gauge and evidence report.

**User Story**: *As a Hindi-speaking citizen, I want a simple interface in my language, so that I can verify media without technical knowledge.*

**Acceptance Criteria**:
1. WHEN the user opens the app THEN the interface SHALL default to Hindi with English toggle
2. WHEN the user completes a verification THEN the Trust Score SHALL be displayed as a clear gauge
3. WHEN the evidence report is ready THEN it SHALL be shown in the user's chosen language
4. WHEN the user is on mobile THEN the app SHALL be installable and work offline for past results
5. WHEN a user needs to submit media THEN they SHALL be able to upload a file or paste a link

**Links**: Requirements FR-13, NFR-19 · Design §1.2, §3.9 · Roadmap Phase A

---

### F14: User Accounts, JWT Auth & Verification History

**Priority**: P1 · **Status**: Planned · **Roadmap**: Phase B

**Description**: Secure user accounts with JWT authentication, role-based access (citizen, journalist, moderator, admin), and per-user verification history.

**User Story**: *As a user, I want my verification history saved securely, so that I can refer back to past checks.*

**Acceptance Criteria**:
1. WHEN a user registers or logs in THEN the system SHALL issue a JWT token
2. WHEN a user requests their history THEN the system SHALL return their past verification records
3. WHEN a role is assigned THEN the system SHALL enforce role-based access control
4. WHEN a token expires THEN the system SHALL require re-authentication
5. WHEN a user is anonymous THEN the system SHALL allow verification without an account

**Links**: Requirements FR-14 · Design §3.9 · Roadmap Phase B

---

### F15: Moderator / Admin Dashboard

**Priority**: P2 · **Status**: Backlog · **Roadmap**: Phase C

**Description**: Dashboard for moderators/admins to review flagged reports, monitor threat-intel cache health, manage model configuration, and view analytics.

**User Story**: *As an administrator, I want visibility into system performance and flagged reports, so that I can maintain accuracy and trust.*

**Acceptance Criteria**:
1. WHEN an admin opens the dashboard THEN the system SHALL show verification volumes and Trust Score distribution
2. WHEN reports are flagged THEN the admin SHALL review and action them
3. WHEN a model underperforms THEN the admin SHALL be able to reconfigure model weights
4. WHEN audit events occur THEN the admin SHALL be able to browse audit logs

**Links**: Requirements FR-15 · Design §3.10 · Roadmap Phase C

---

## 4. Feature → Requirement → Design Traceability

| Feature | Requirement | Design Component | Phase |
|---------|-------------|------------------|-------|
| F1 Multimodal Media Upload | FR-01 | §3.1 Upload & Intake | A |
| F2 Image Deepfake Detection | FR-02 | §3.3 Image Detector | A |
| F3 Video Deepfake Detection | FR-03 | §3.4 Video Detector | A |
| F4 Voice Clone Detection | FR-04 | §3.5 Audio Detector | A |
| F5 Media Forensics Engine | FR-05 | §3.2, §3.3–3.5 | A |
| F6 OCR Text Extraction | FR-06 | §3.6 OCR/NLP | B |
| F7 Scam Intent Classifier | FR-07 | §3.6 OCR/NLP | B |
| F8 Threat Intelligence | FR-08 | §3.7 Threat Intel | A |
| F9 Unified Trust Score | FR-09 | §3.8 Risk Engine | A |
| F10 Explainable Evidence Report | FR-10 | §3.8 Gemini 2.5 | A |
| F11 Recommended Action | FR-11 | §3.8 Risk Engine | A |
| F12 I4C/1930 Reporting & Audit | FR-12 | §3.10 Reporting & Audit | B |
| F13 Hindi-First PWA | FR-13 | §1.2, §3.9 | A |
| F14 Accounts & History | FR-14 | §3.9 User Mgmt | B |
| F15 Admin Dashboard | FR-15 | §3.10 Reporting & Audit | C |

## 5. Feature Delivery Mapping

| Phase | Features |
|-------|----------|
| **Phase A (Hackathon MVP)** | F1, F2, F3, F4, F5, F8, F9, F10, F11, F13 |
| **Phase B (Pilot)** | F6, F7, F12, F14 |
| **Phase C (Scale)** | F15 |

---

**Document Version:** 1.0  
**Last Updated:** August 2026  
**Status:** Ready for Hackathon Submission