# Requirements Document: SatyaKavach – AI-Powered Deepfake & Manipulated Media Detection

> **Connected Documents**: [features.md](./features.md) (feature catalogue & traceability) · [design.md](./design.md) (architecture & design) · [roadmap.md](./roadmap.md) (delivery phases)
>
> This document defines the functional and non-functional requirements of SatyaKavach. Every requirement maps to a feature (FR-XX ↔ FXX in [features.md](./features.md)) and an architectural component (see [design.md](./design.md)).

## 1. Introduction

### 1.1 Problem Definition

Generative AI can now create highly realistic fake images, videos, and voices that are difficult for ordinary users to distinguish from authentic content. Deepfakes are increasingly used to spread misinformation, impersonate individuals, manipulate public opinion, and damage trust in digital media. Citizens, journalists, educators, and organizations need an accessible way to verify whether media is authentic or manipulated before acting on it.

Key challenges include:

- **Realistic Deepfakes**: AI-generated media quality has improved significantly, making manual detection increasingly difficult
- **Rapid Misinformation Spread**: Manipulated videos, images, and audio can reach millions of users before verification occurs
- **Lack of Citizen-Friendly Tools**: Most deepfake detection solutions are research-focused or enterprise-oriented rather than accessible to everyday users
- **Need for Explainable Verification**: Users need evidence-backed explanations, not just a "fake" or "real" label

**Quantified Impact**:
- **500M+** deepfake videos and images expected to circulate across digital platforms globally each year
- **3X faster** spread of highly engaging manipulated media compared to verified content
- **96%** of detected deepfakes in public datasets contain manipulated faces
- Manual detection is no longer reliable as deepfake realism grows

*Sources: DFDC, FaceForensics++, FakeAVCeleb, DeepFakeBench*

### 1.2 Why Existing Solutions Fail

- **Image-only tools**: Verify images only, ignore video and audio
- **Video-only tools**: Verify videos only, ignore images and audio
- **Audio / voice-clone tools**: Detect cloned voices only
- **Research models**: Highly accurate but difficult for citizens to use
- **The Gap**: Users need one simple platform that can verify images, videos, and audio with explainable results — a unified media verification layer

## 2. Glossary

- **SatyaKavach_System**: The complete AI-powered deepfake & manipulated media verification platform
- **Trust_Score**: A unified 0–100 confidence score of media authenticity
- **Verdict**: HIGH_TRUST / UNCERTAIN / LOW_TRUST classification derived from the Trust Score
- **Risk_Engine**: Multimodal fusion engine combining all AI signals into a unified Trust Score
- **Evidence_Report**: Explainable, plain-language report citing the signals and artifacts behind a verdict
- **Recommended_Action**: A clear next step (verify / cross-check / do not share / report) per verdict
- **Image_Deepfake_Detector**: EfficientNet + XceptionNet + Gemini Vision ensemble for face manipulation
- **Video_Deepfake_Detector**: TimeSformer + Video Swin Transformer + Gemini Vision temporal analysis
- **Audio_Deepfake_Detector**: Wav2Vec2 + Whisper + audio spectrogram analysis for voice clones
- **Media_Forensics_Engine**: Cross-modal analysis for tampering, editing, and manipulation artifacts
- **OCR_Extractor**: EasyOCR-based text extraction from screenshots and images
- **Scam_Classifier**: NLP model for message & intent analysis and scam detection
- **Threat_Intelligence_Service**: External signals (VirusTotal, Google Safe Browsing, PhishTank, Domain Reputation)
- **Threat_Intelligence_Cache**: Cached URL/domain reputation results to reduce redundant lookups
- **I4C_1930_Ecosystem**: Indian cyber-fraud reporting ecosystem for citizen reporting
- **Hindi_First_UI**: Bilingual (Hindi/English), citizen-friendly, mobile-first interface

## 3. Target Users & Personas

### 3.1 Primary Users

**Persona 1: Social Media Citizen**
- Age: 18–55, uses WhatsApp/Instagram/Facebook daily
- Moderate digital literacy, speaks Hindi or regional language
- Needs: Verify forwarded videos, images, and voice messages before sharing
- Constraints: Limited understanding of AI/deepfakes; wants simple answers and evidence

**Persona 2: Journalist / Fact-Checker**
- Age: 25–50, professionally verifies media
- High digital literacy, English + regional languages
- Needs: Fast, credible, reproducible verification of images, videos, and audio
- Constraints: Needs evidence export, high accuracy, and low false-positive rates

**Persona 3: Student / Educator**
- Age: 15–60, uses digital media for study and teaching
- Moderate digital literacy
- Needs: Verify sources, teach media literacy, understand how detection works
- Constraints: Needs explainable results and multi-language support

**Persona 4: Government / Public Institution Official**
- Age: 30–60, manages official communications
- High digital literacy
- Needs: Protect official channels from impersonation; verify circulating content
- Constraints: Needs audit trails, I4C/1930 reporting, and reliable verdicts

### 3.2 Secondary Users

- **Community / NGO Volunteers**: Assist citizens with verification
- **Journalists' editorial desks**: Batch verification workflows
- **Platform moderators**: Review flagged reports and maintain model configuration

## 4. Goals & Measurable Success Metrics

### 4.1 Hackathon MVP Goals

- **Media Coverage**: Verify images, videos, and audio in one unified platform
- **Verdict Quality**: Provide Trust Score + Verdict + Evidence Report + Recommended Action for every analysis
- **Explainability**: 100% of verdicts accompanied by an evidence-backed explanation
- **Accessibility**: Hindi-first interface; works on mobile via PWA

### 4.2 Success Metrics

- **Accuracy**: 90%+ detection accuracy on test datasets (DFDC, FaceForensics++, Celeb-DF v2, ASVspoof 2019)
- **Fusion**: 95%+ consistency between Trust Score and the ground truth of benchmark media
- **Performance**: Image verdict < 10s, video verdict < 60s, audio verdict < 30s (async)
- **Explainability**: 100% of completed verifications produce an Evidence Report
- **Availability**: 99.5% uptime during demo
- **Scalability**: Handle concurrent verifications without degradation (stateless APIs + async workers)

## 5. Functional Requirements

> Each functional requirement (FR) maps to a feature (FXX) in [features.md](./features.md).

### Requirement FR-01: Multimodal Media Upload (Image • Video • Audio)

**User Story:** As a citizen, I want to upload any suspicious media (image, video, audio, screenshot, or link) in one place, so that I can verify it without switching between tools.

#### Acceptance Criteria

1. WHEN a user uploads an image, video, audio, screenshot, or link THEN the SatyaKavach_System SHALL accept it and start analysis
2. WHEN a file is not a supported type THEN the SatyaKavach_System SHALL reject it with a clear error
3. WHEN an upload succeeds THEN the SatyaKavach_System SHALL return a unique media ID and job status immediately
4. WHEN the same media is uploaded again THEN the SatyaKavach_System SHALL return the cached result (SHA-256 deduplication)
5. WHEN a user submits without an account THEN the SatyaKavach_System SHALL allow anonymous verification

**Maps to**: Feature F1 · Design §3.1

---

### Requirement FR-02: Deepfake Face Detection (Image)

**User Story:** As a social media user, I want to know if a shared photo has been manipulated, so that I do not spread fake content.

#### Acceptance Criteria

1. WHEN an image is analyzed THEN the SatyaKavach_System SHALL produce a Manipulation Score (0–1)
2. WHEN the Manipulation Score > 0.5 THEN the SatyaKavach_System SHALL classify the image as "Fake"
3. WHEN the Manipulation Score ≤ 0.5 THEN the SatyaKavach_System SHALL classify the image as "Real"
4. WHEN multiple faces are present THEN the SatyaKavach_System SHALL report per-face manipulation evidence
5. WHEN model confidence is low THEN the SatyaKavach_System SHALL flag the result for human review

**Maps to**: Feature F2 · Design §3.3 · Datasets: FaceForensics++, Celeb-DF v2, DFDC

---

### Requirement FR-03: Video Deepfake Detection

**User Story:** As a journalist, I want to verify a video before reporting on it, so that I do not publish manipulated footage.

#### Acceptance Criteria

1. WHEN a video is analyzed THEN the SatyaKavach_System SHALL extract keyframes and face tracks
2. WHEN temporal manipulation is detected THEN the SatyaKavach_System SHALL flag affected frames
3. WHEN a video contains audio THEN the SatyaKavach_System SHALL analyze the audio track
4. WHEN a video passes analysis THEN the SatyaKavach_System SHALL return a Video Authenticity Score
5. WHEN manipulation is found THEN the SatyaKavach_System SHALL list the frame locations as evidence

**Maps to**: Feature F3 · Design §3.4 · Datasets: FaceForensics++, DFDC, DeepFakeTIMIT

---

### Requirement FR-04: AI Voice Clone Detection

**User Story:** As a citizen, I want to verify a voice message, so that I am not deceived by a cloned voice.

#### Acceptance Criteria

1. WHEN audio is analyzed THEN the SatyaKavach_System SHALL produce a Voice Clone Detection result
2. WHEN audio is analyzed THEN the SatyaKavach_System SHALL produce an Audio Authenticity Score (0–1)
3. WHEN speech is present THEN the SatyaKavach_System SHALL transcribe it (Hindi/English) as evidence
4. WHEN a voice clone is detected THEN the SatyaKavach_System SHALL flag the audio as high risk
5. WHEN audio quality is poor THEN the SatyaKavach_System SHALL note reduced confidence

**Maps to**: Feature F4 · Design §3.5 · Datasets: ASVspoof 2019, FakeAVCeleb, WaveFake

---

### Requirement FR-05: Media Forensics Engine

**User Story:** As a fact-checker, I want forensic signals about how media may have been manipulated, so that I can assess credibility.

#### Acceptance Criteria

1. WHEN media is analyzed THEN the SatyaKavach_System SHALL detect editing artifacts (blending, splicing, compression traces)
2. WHEN tampering evidence exists THEN the SatyaKavach_System SHALL list the artifacts found
3. WHEN metadata conflicts with content THEN the SatyaKavach_System SHALL flag the inconsistency
4. WHEN no artifacts are found THEN the SatyaKavach_System SHALL report "no manipulation artifacts detected"

**Maps to**: Feature F5 · Design §3.2, §3.3, §3.4, §3.5

---

### Requirement FR-06: OCR Text Extraction (Screenshot / Image Text)

**User Story:** As a citizen, I want to verify a screenshot of a message, so that I can analyze its content.

#### Acceptance Criteria

1. WHEN a screenshot is uploaded THEN the SatyaKavach_System SHALL extract embedded text with EasyOCR
2. WHEN text contains Hindi or English THEN the SatyaKavach_System SHALL extract both
3. WHEN text is extracted THEN the SatyaKavach_System SHALL preserve bounding-box coordinates as evidence
4. WHEN no readable text exists THEN the SatyaKavach_System SHALL report that no text was found

**Maps to**: Feature F6 · Design §3.6

---

### Requirement FR-07: NLP / Scam Intent Classification

**User Story:** As a user, I want to know whether a suspicious message is a scam, so that I can avoid fraud.

#### Acceptance Criteria

1. WHEN text or transcription is available THEN the SatyaKavach_System SHALL classify the message intent
2. WHEN scam indicators (urgency, financial ask, impersonation, OTP) are found THEN the SatyaKavach_System SHALL list them
3. WHEN scam likelihood is high THEN the SatyaKavach_System SHALL raise the overall risk contribution
4. WHEN the message is benign THEN the SatyaKavach_System SHALL report low scam likelihood

**Maps to**: Feature F7 · Design §3.6

---

### Requirement FR-08: Threat Intelligence (Link / URL Verification)

**User Story:** As a user, I want to know whether a link in a message is malicious, so that I do not click on phishing or malware URLs.

#### Acceptance Criteria

1. WHEN a link is submitted THEN the SatyaKavach_System SHALL query VirusTotal, Google Safe Browsing, PhishTank, and Domain Reputation
2. WHEN a link is flagged by any source THEN the SatyaKavach_System SHALL raise the threat score
3. WHEN a link was checked recently THEN the SatyaKavach_System SHALL return the cached verdict within TTL
4. WHEN external threat-intel APIs are unavailable THEN the SatyaKavach_System SHALL degrade gracefully

**Maps to**: Feature F8 · Design §3.7

---

### Requirement FR-09: Unified Trust Score & Verdict

**User Story:** As a citizen, I want one simple number that tells me how much I can trust media, so that I can act confidently.

#### Acceptance Criteria

1. WHEN at least one signal is available THEN the SatyaKavach_System SHALL compute a Trust Score (0–100)
2. WHEN the score is ≥ 80 THEN the SatyaKavach_System SHALL classify as HIGH_TRUST
3. WHEN the score is 50–79 THEN the SatyaKavach_System SHALL classify as UNCERTAIN
4. WHEN the score is < 50 THEN the SatyaKavach_System SHALL classify as LOW_TRUST
5. WHEN a signal is unavailable THEN the SatyaKavach_System SHALL re-normalize weights over available signals
6. WHEN the verdict is UNCERTAIN THEN the SatyaKavach_System SHALL recommend further verification

**Maps to**: Feature F9 · Design §3.8, §4.2

---

### Requirement FR-10: Explainable Evidence Report

**User Story:** As a user, I want to understand why a verdict was reached, so that I can trust the result — not just a label.

#### Acceptance Criteria

1. WHEN a verdict is produced THEN the SatyaKavach_System SHALL generate a plain-language Evidence Report
2. WHEN artifacts influenced the verdict THEN the report SHALL cite them with visual evidence
3. WHEN a verdict is HIGH_TRUST THEN the report SHALL explain which checks passed
4. WHEN a verdict is LOW_TRUST THEN the report SHALL highlight the strongest manipulation signals
5. THE Evidence Report SHALL be available in Hindi and English

**Maps to**: Feature F10 · Design §3.8 (Gemini 2.5 Explainable Layer)

---

### Requirement FR-11: Recommended Action

**User Story:** As a citizen, I want to know what to do next, so that I can act responsibly on the result.

#### Acceptance Criteria

1. WHEN the verdict is HIGH_TRUST THEN the SatyaKavach_System SHALL recommend "likely authentic — verify context before sharing"
2. WHEN the verdict is UNCERTAIN THEN the SatyaKavach_System SHALL recommend "further verification recommended"
3. WHEN the verdict is LOW_TRUST THEN the SatyaKavach_System SHALL recommend "do not share — report to I4C/1930"
4. WHEN LOW_TRUST media is detected THEN the SatyaKavach_System SHALL offer a one-tap report action

**Maps to**: Feature F11 · Design §3.8

---

### Requirement FR-12: I4C / 1930 Reporting & Audit

**User Story:** As a citizen, I want to report a confirmed deepfake to the authorities, so that action can be taken.

#### Acceptance Criteria

1. WHEN a user initiates a report THEN the SatyaKavach_System SHALL export the evidence package
2. WHEN a report is submitted THEN the SatyaKavach_System SHALL record it in the audit log
3. WHEN a report is submitted THEN the SatyaKavach_System SHALL confirm submission to the user
4. WHEN a user has no account THEN the SatyaKavach_System SHALL still allow anonymous reporting

**Maps to**: Feature F12 · Design §3.10

---

### Requirement FR-13: Hindi-First Citizen Interface (PWA)

**User Story:** As a Hindi-speaking citizen, I want a simple interface in my language, so that I can verify media without technical knowledge.

#### Acceptance Criteria

1. WHEN the user opens the app THEN the interface SHALL default to Hindi with an English toggle
2. WHEN a verification completes THEN the Trust Score SHALL be displayed as a clear gauge
3. WHEN the evidence report is ready THEN it SHALL be shown in the user's chosen language
4. WHEN the user is on mobile THEN the app SHALL be installable (PWA) and usable offline for past results
5. WHEN the user needs to submit media THEN they SHALL be able to upload a file or paste a link

**Maps to**: Feature F13 · Design §1.2, §3.9

---

### Requirement FR-14: User Accounts, JWT Auth & History

**User Story:** As a user, I want my verification history saved securely, so that I can refer back to past checks.

#### Acceptance Criteria

1. WHEN a user registers or logs in THEN the SatyaKavach_System SHALL issue a JWT token
2. WHEN a user requests their history THEN the SatyaKavach_System SHALL return past verification records
3. WHEN a role is assigned THEN the SatyaKavach_System SHALL enforce role-based access control
4. WHEN a token expires THEN the SatyaKavach_System SHALL require re-authentication
5. WHEN a user is anonymous THEN the SatyaKavach_System SHALL allow verification without an account

**Maps to**: Feature F14 · Design §3.9

---

### Requirement FR-15: Moderator / Admin Dashboard

**User Story:** As an administrator, I want visibility into system performance and flagged reports, so that I can maintain accuracy and trust.

#### Acceptance Criteria

1. WHEN an admin opens the dashboard THEN the SatyaKavach_System SHALL show verification volumes and Trust Score distribution
2. WHEN reports are flagged THEN the admin SHALL be able to review and action them
3. WHEN a model underperforms THEN the admin SHALL be able to reconfigure model weights
4. WHEN audit events occur THEN the admin SHALL be able to browse audit logs

**Maps to**: Feature F15 · Design §3.10

## 6. Non-Functional Requirements

> Each non-functional requirement (NFR) applies across all features unless stated otherwise.

### Requirement NFR-16: Performance & Responsiveness

**User Story:** As a user, I want fast verification results, so that I can act quickly on suspicious media.

#### Acceptance Criteria

1. THE SatyaKavach_System SHALL return image verdicts within 10 seconds (async target)
2. THE SatyaKavach_System SHALL return video verdicts within 60 seconds
3. THE SatyaKavach_System SHALL return audio verdicts within 30 seconds
4. WHEN the frontend loads THEN the page SHALL be interactive within 3 seconds on mobile
5. THE SatyaKavach_System SHALL process multiple concurrent verifications via async workers without queue blocking

### Requirement NFR-17: Scalability

**User Story:** As an operator, I want the platform to scale during misinformation spikes, so that it remains available.

#### Acceptance Criteria

1. THE SatyaKavach_System SHALL use stateless services to enable horizontal scaling
2. THE SatyaKavach_System SHALL process verification jobs asynchronously (queue + workers)
3. THE SatyaKavach_System SHALL scale AI services independently (modular AI services)
4. THE SatyaKavach_System SHALL cache frequent lookups (SHA-256 dedup, threat-intel cache)
5. THE SatyaKavach_System SHALL handle a 10x traffic spike without architecture changes

### Requirement NFR-18: Security & Privacy

**User Story:** As a user sharing media and personal data, I want my data to be secure and private, so that I can trust the platform.

#### Acceptance Criteria

1. THE SatyaKavach_System SHALL encrypt all data in transit (HTTPS / TLS)
2. THE SatyaKavach_System SHALL encrypt all evidence at rest (AWS S3 SSE-KMS, PostgreSQL encryption)
3. THE SatyaKavach_System SHALL implement input validation and secure file handling (MIME, magic bytes, size limits)
4. THE SatyaKavach_System SHALL implement role-based access control (citizen / journalist / moderator / admin)
5. THE SatyaKavach_System SHALL log all verification and security events in audit logs
6. WHEN a user requests data deletion THEN the SatyaKavach_System SHALL remove personal data within a defined period
7. THE SatyaKavach_System SHALL not retain evidence beyond 90 days unless explicitly consented
8. THE SatyaKavach_System SHALL scan uploaded files with VirusTotal before analysis

### Requirement NFR-19: Accessibility & Inclusion

**User Story:** As a low-literacy or disabled user, I want an accessible interface, so that I can verify media independently.

#### Acceptance Criteria

1. THE SatyaKavach_System SHALL support screen readers for visually impaired users
2. THE SatyaKavach_System SHALL provide text alternatives for all voice/audio content
3. THE SatyaKavach_System SHALL support adjustable text size and high-contrast modes
4. THE SatyaKavach_System SHALL use plain, non-technical language (6th-grade reading level)
5. THE SatyaKavach_System SHALL be usable on low-end mobile devices via PWA
6. THE SatyaKavach_System SHALL comply with WCAG 2.1 Level AA where applicable

### Requirement NFR-20: Maintainability & Extensibility

**User Story:** As a maintainer, I want modular, well-documented code, so that I can add models, languages, and signals efficiently.

#### Acceptance Criteria

1. THE SatyaKavach_System SHALL use a modular AI service architecture with clear API contracts
2. THE SatyaKavach_System SHALL register AI models in a model registry for easy addition
3. THE SatyaKavach_System SHALL provide API documentation (OpenAPI/Swagger)
4. THE SatyaKavach_System SHALL implement comprehensive logging for debugging
5. THE SatyaKavach_System SHALL use configuration files for environment-specific settings
6. THE SatyaKavach_System SHALL support adding languages without code changes (externalized content)

### Requirement NFR-21: Reliability & Graceful Degradation

**User Story:** As a user, I want the system to remain usable even if some AI services fail, so that I still get a result.

#### Acceptance Criteria

1. WHEN a single AI service fails THEN the SatyaKavach_System SHALL continue with remaining signals
2. WHEN an external threat-intel API fails THEN the SatyaKavach_System SHALL fall back to cached results or omit the signal
3. WHEN a model returns low confidence THEN the SatyaKavach_System SHALL mark the result UNCERTAIN rather than guessing
4. THE SatyaKavach_System SHALL implement retry with exponential backoff for transient failures
5. THE SatyaKavach_System SHALL implement circuit breakers for unreliable external integrations

## 7. Constraints

### 7.1 Technical Constraints

- **Frontend**: Must use React.js + TypeScript + Tailwind CSS (PWA)
- **Backend**: Must use FastAPI (Python) with REST APIs and JWT authentication
- **AI Models**: Must use the specified stack (Gemini, EfficientNet, XceptionNet, TimeSformer, Video Swin Transformer, Whisper, Wav2Vec2, EasyOCR) or pre-trained equivalents
- **Datasets**: Detection validated against FaceForensics++, Celeb-DF v2, DFDC, DeepFakeTIMIT, ASVspoof 2019, FakeAVCeleb, WaveFake
- **Infrastructure**: Docker, AWS EC2, AWS S3, Nginx (hackathon constraint)
- **Timeline**: MVP must be demonstrable within hackathon timeframe (48–72 hours for prototype)

### 7.2 Regulatory Constraints

- **Data Privacy**: Must comply with applicable Indian data-protection principles (DPDP Act 2023 alignment)
- **Consent**: Explicit user consent required for storing media and personal data
- **Retention**: Media/evidence retention limited to 90 days unless explicitly consented
- **Reporting**: Confirmed deepfake reports handed to the I4C / 1930 ecosystem

### 7.3 Data Constraints

- **Training Data**: Public benchmark datasets only (no proprietary real-world deepfake databases)
- **Threat Intel**: External APIs (VirusTotal, Google Safe Browsing, PhishTank) may have rate limits and quotas
- **Language Support**: Hindi-first with English; additional languages as extendable content

### 7.4 Operational Constraints

- **Demo Environment**: AWS free-tier / hackathon credits; evidence stored in S3 with lifecycle rules
- **Async Processing**: Video/audio analysis run asynchronously; users poll for results
- **Moderation**: Human review required for borderline (UNCERTAIN) verdicts

## 8. Risks & Mitigation Strategies

### 8.1 Technical Risks

**Risk 1: Deepfake Detection Accuracy Drift**
- **Impact**: High — false verdicts undermine trust
- **Probability**: Medium — deepfake generation techniques evolve
- **Mitigation**:
  - Use multi-model ensembles (not a single model)
  - Corroborate with Gemini Vision / Gemini 2.5 reasoning
  - Continuously benchmark against DeepFakeBench and updated datasets
  - Add an UNCERTAIN verdict zone instead of forcing a binary decision

**Risk 2: Voice Clone False Positives / Negatives**
- **Impact**: High — wrong audio verdicts
- **Probability**: Medium — noisy, low-quality audio inputs
- **Mitigation**:
  - Combine Wav2Vec2 + Whisper + spectrogram signals
  - Reduce confidence on poor-quality audio and surface it in the report
  - Human review path for borderline audio

**Risk 3: Threat-Intel Dependency**
- **Impact**: Medium — link verification unavailable
- **Probability**: Medium — API rate limits/quotas
- **Mitigation**:
  - Cache results with TTL (Threat Intelligence Cache)
  - Multi-vendor fusion (VirusTotal + Safe Browsing + PhishTank + Domain Reputation)
  - Graceful degradation to AI-only signals

**Risk 4: Scalability Under Misinformation Spike**
- **Impact**: Medium — queue backlog delays verdicts
- **Probability**: Medium — viral content surges
- **Mitigation**:
  - Stateless APIs + async worker pool
  - SHA-256 deduplication to avoid re-analyzing the same media
  - Modular AI services scaled independently

### 8.2 Data Quality Risks

**Risk 5: Biased / Unrepresentative Training Data**
- **Impact**: High — models may underperform on certain demographics, lighting, or languages
- **Probability**: Medium
- **Mitigation**:
  - Use diverse public benchmarks (DFDC, FaceForensics++, Celeb-DF v2)
  - Continuously evaluate with DeepFakeBench
  - Report confidence so users know when to seek human review

**Risk 6: Manipulated Media Without Faces**
- **Impact**: Medium — 96% of deepfakes contain faces, but non-face manipulation exists
- **Probability**: Low
- **Mitigation**:
  - Media Forensics Engine covers non-face tampering (artifacts, metadata, compression)
  - OCR/NLP + threat-intel cover text and link manipulation

### 8.3 Ethical & Trust Risks

**Risk 7: User Privacy Concerns**
- **Impact**: High — privacy breaches destroy trust
- **Probability**: Low — with proper safeguards
- **Mitigation**:
  - Anonymous verification supported
  - Metadata stripping on upload
  - Encrypted storage (SSE-KMS) and 90-day retention
  - Transparent privacy policy in simple language
  - Audit logs without exposing media content

**Risk 8: Over-Trust in AI Verdicts**
- **Impact**: High — users may treat verdicts as absolute truth
- **Probability**: Medium
- **Mitigation**:
  - Explainable Evidence Reports, not just labels
  - UNCERTAIN verdict zone + "further verification recommended" guidance
  - Clear disclaimers about confidence and limitations
  - Recommended action framing (verify / report) rather than absolute judgments

**Risk 9: Misuse of the Platform**
- **Impact**: Medium — platform used to "whitewash" media as authentic
- **Probability**: Low
- **Mitigation**:
  - Show confidence and model breakdown for every verdict
  - Human review for borderline cases
  - Audit logging of all verifications

### 8.4 Adoption Risks

**Risk 10: Low Adoption by Citizens**
- **Impact**: High — platform fails if users don't use it
- **Probability**: Medium
- **Mitigation**:
  - Hindi-first, simple, mobile-first PWA
  - Voice/screenshot/message/link intake — meet users where they are
  - Clear, visual Trust Score gauge (no technical jargon)
  - One-tap I4C/1930 reporting for tangible civic value

## 9. Ethical & Responsible AI Design

### 9.1 Privacy-First Design

- **Minimal Data Collection**: Collect only what is needed for verification
- **Anonymous Access**: Verification works without an account
- **Metadata Stripping**: User/device metadata removed on upload
- **Encrypted Storage**: All evidence encrypted at rest (SSE-KMS)
- **Retention Limits**: Evidence deleted after 90 days unless explicitly consented
- **No Unwanted Sharing**: Media never shared with third parties without consent

### 9.2 Explainable AI

- **Evidence-Backed Verdicts**: Every decision backed by cited evidence
- **Per-Model Breakdown**: Users can inspect individual model scores
- **Plain-Language Reasoning**: Gemini 2.5 generates simple explanations (Hindi/English)
- **Confidence Transparency**: Low-confidence results flagged as UNCERTAIN
- **Human Review**: Borderline cases routed for human review

### 9.3 Bias Mitigation

- **Diverse Datasets**: Evaluation across multiple public benchmarks
- **Confidence Reporting**: Surface low-confidence results honestly
- **Model Breakdown Transparency**: Reveal which model drove the verdict
- **Continuous Evaluation**: Benchmark against DeepFakeBench to catch drift

### 9.4 Safety & Boundaries

- **No Absolute Truth Claims**: Verdicts framed as confidence, not certainty
- **Action-Oriented Guidance**: Recommendations that encourage verification and reporting
- **Clear Disclaimers**: Communicate limitations of automated detection
- **Responsible Reporting**: Confirmed deepfakes routed to I4C/1930 rather than public shaming
- **Detection of Manipulated Content**: Never used to generate or aid fabrication

### 9.5 Accessibility & Inclusion

- **Hindi-First**: Bilingual default for broad Indian reach
- **Simple Language**: 6th-grade reading level for evidence reports
- **Multiple Inputs**: Voice, screenshot, message, link, and file upload
- **Mobile-First PWA**: Works on low-end devices
- **Economic Accessibility**: Free for citizens

## 10. Novelty & Differentiation

### 10.1 Key Innovations

**1. One Unified Verification Layer**
- Unlike fragmented image/video/audio tools, SatyaKavach verifies all modalities in one platform
- A single Trust Score replaces confusing, tool-specific outputs

**2. Multimodal AI Fusion**
- Combines image (EfficientNet/XceptionNet), video (TimeSformer/Swin), audio (Wav2Vec2/Whisper), OCR/NLP, and threat-intel signals into one explainable score
- Re-normalizes gracefully when some signals are unavailable

**3. Explainable & Action-Oriented**
- Gemini 2.5 explains every verdict with cited evidence — not just a "fake/real" label
- Recommends a clear next action (verify / cross-check / report)

**4. Citizen-First & Hindi-First**
- Designed for everyday citizens, not researchers
- Works on mobile (PWA), supports voice/screenshot/message/link intake

**5. Security & Fraud Ecosystem Integration**
- Threat-intel enrichment (VirusTotal, Safe Browsing, PhishTank)
- One-tap reporting to the I4C / 1930 ecosystem

### 10.2 Competitive Advantages

| Feature | SatyaKavach | Image-only tools | Video-only tools | Audio-only tools | Research models |
|---------|-------------|------------------|------------------|------------------|-----------------|
| Image Verification | ✅ | ✅ | ❌ | ❌ | ⚠️ |
| Video Verification | ✅ | ❌ | ✅ | ❌ | ⚠️ |
| Audio Verification | ✅ | ❌ | ❌ | ✅ | ⚠️ |
| Unified Trust Score | ✅ | ❌ | ❌ | ❌ | ❌ |
| Explainable Results | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ |
| Citizen-Friendly | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ |
| Hindi-First UI | ✅ | ❌ | ❌ | ❌ | ❌ |
| Threat Intelligence | ✅ | ❌ | ❌ | ❌ | ❌ |
| I4C/1930 Reporting | ✅ | ❌ | ❌ | ❌ | ❌ |

## 11. AI Models, Datasets & External Services Mapping

### 11.1 AI Model Stack

| Signal | Models | Output |
|--------|--------|--------|
| **Image Deepfake** | Gemini Vision, EfficientNet, XceptionNet | Manipulation Score, Fake/Real Classification |
| **Video Deepfake** | TimeSformer, Video Swin Transformer, Gemini Vision | Frame-level Detection, Video Authenticity Score |
| **Audio Deepfake** | Whisper, Wav2Vec2, Audio Spectrogram Analysis | Voice Clone Detection, Audio Authenticity Score |
| **Multimodal Reasoning** | Gemini 2.5, Explainable AI Layer | Trust Score, Evidence Report, Final Verdict |
| **Text Extraction** | EasyOCR | Screenshot/image text extraction |
| **Scam Classification** | NLP / Scam Classifier | Message & intent analysis |

### 11.2 Datasets

| Detection Type | Datasets |
|----------------|----------|
| Image Deepfake | FaceForensics++, Celeb-DF v2, DFDC Dataset |
| Video Deepfake | FaceForensics++, DFDC, DeepFakeTIMIT |
| Audio Deepfake | ASVspoof 2019, FakeAVCeleb, WaveFake |
| Multimodal Reasoning | Image, Video, Audio + Extracted Metadata |
| Continuous Benchmarking | DeepFakeBench |

### 11.3 External Threat Intelligence Services

| Service | Purpose |
|---------|---------|
| VirusTotal API | URL/domain/file reputation |
| Google Safe Browsing | Known malicious URL detection |
| PhishTank | Phishing URL intelligence |
| Domain Reputation | Additional URL risk signals |

### 11.4 Architecture Layers (see [design.md](./design.md) §2)

| Layer | Components |
|-------|------------|
| **Presentation** | React + TypeScript + Tailwind PWA, Hindi-first, voice/upload interface |
| **Backend & Orchestration** | FastAPI, REST APIs, JWT, Risk Engine, async processing |
| **AI & Intelligence** | Gemini, Whisper, EasyOCR, NLP/Scam Classifier, detection models |
| **Data** | PostgreSQL, AWS S3, Threat Intelligence Cache, Audit Logs |
| **Threat Intelligence** | VirusTotal, Safe Browsing, PhishTank, Domain Reputation |
| **Infrastructure** | Docker, AWS EC2, AWS S3, Nginx (HTTPS, JWT, input validation, secure file handling) |

## 12. Deployment Strategy

### Phase A: Hackathon MVP (48–72 hours)

**Scope**:
- All P0 features (F1–F5, F8–F11, F13)
- 2 languages (Hindi, English)
- Sample media from benchmark datasets (FaceForensics++, ASVspoof, FakeAVCeleb)
- Mock threat-intel responses if API quotas limited

**Demo Scenario**:
1. User uploads a manipulated image → Image Deepfake Detector scores it
2. Risk Engine fuses signals → Trust Score 15/100 → LOW_TRUST
3. Gemini 2.5 generates Hindi evidence report with highlighted artifacts
4. Recommended action: "Do not share — report to I4C/1930"
5. User verifies an authentic video → HIGH_TRUST with passing checks explained

### Phase B: Public Pilot (1–3 months)

**Scope**:
- Add OCR (F6), Scam Classifier (F7), I4C/1930 reporting (F12), user accounts (F14)
- Real threat-intel API integration with caching
- Multi-language evidence reports (Tamil, Telugu, Bengali)
- Journalist/fact-checker workflows

### Phase C: Nationwide Scale (3–12 months)

**Scope**:
- Admin dashboard (F15)
- Real-time video verification
- Government/media partnerships
- Deepfake trend monitoring and misinformation-event alerts

## 13. Appendix

### 13.1 Sample Verification Flow (Image)

```
User uploads image of a manipulated face
         ↓
Intake & validation → S3 evidence storage → enqueue job
         ↓
Preprocessing → face detection/cropping
         ↓
EfficientNet + XceptionNet → per-face manipulation scores
Gemini Vision → manipulation corroboration
         ↓
Image Manipulation Score = 0.86 → "Fake"
         ↓
Risk Engine → Trust Score 18/100 → LOW_TRUST
         ↓
Gemini 2.5 → Evidence Report (Hindi/English) with cited artifacts
         ↓
Recommended Action: "Do not share. Report to I4C/1930."
```

### 13.2 Sample Evidence Report (Abridged)

```
विश्वास स्कोर (Trust Score): 18/100 → LOW_TRUST (कम भरोसा)

क्यों (Why):
- चेहरा ब्लेंडिंग आर्टिफैक्ट पाया गया (EfficientNet: 0.86)
- छवि संपीड़न विसंगतियाँ (XceptionNet: 0.79)
- जेमिनी विज़न ने संपादन के निशान पुष्टि की (Gemini Vision: 0.88)

सिफारिश (Recommended Action):
- इस मीडिया को साझा न करें
- I4C/1930 पर रिपोर्ट करें

(English: Trust Score 18/100 — LOW_TRUST. Face blending artifacts detected (EfficientNet 0.86), compression anomalies (XceptionNet 0.79), editing traces confirmed by Gemini Vision (0.88). Do not share. Report to I4C/1930.)
```

### 13.3 References

- DFDC (Deepfake Detection Challenge) Dataset
- FaceForensics++ Dataset
- Celeb-DF v2 Dataset
- ASVspoof 2019 Challenge
- FakeAVCeleb & WaveFake Datasets
- DeepFakeBench Benchmark
- Digital Personal Data Protection Act, 2023 (alignment)
- WCAG 2.1 Accessibility Guidelines
- AWS Well-Architected Framework
- I4C / 1930 Cyber Fraud Reporting Ecosystem

---

**Document Version:** 1.0  
**Last Updated:** August 2026  
**Status:** Ready for Hackathon Submission