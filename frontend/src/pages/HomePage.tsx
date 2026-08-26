import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLang } from '../App';
import { t } from '../i18n/translations';
import FileUpload from '../components/FileUpload';
import Icon, { type IconName } from '../components/Icon';
import { uploadAPI, verificationAPI } from '../services/api';

export default function HomePage() {
  const { lang } = useLang();
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState('');

  const handleFileSelect = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setUploadProgress(t('preprocessing', lang));

    try {
      const result = await uploadAPI.uploadFile(file, lang);
      if (result.status === 'complete') {
        navigate(`/result/${result.media_id}`);
      } else {
        setUploadProgress(t('analyzing', lang));
        pollStatus(result.media_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setIsUploading(false);
    }
  };

  const handleLinkSubmit = async (url: string) => {
    setIsUploading(true);
    setError(null);
    setUploadProgress(t('analyzing', lang));

    try {
      const result = await uploadAPI.submitLink(url, lang);
      navigate(`/result/${result.media_id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Link verification failed.');
      setIsUploading(false);
    }
  };

  const pollStatus = async (mediaId: string) => {
    let attempts = 0;
    const poll = async () => {
      try {
        const status = await verificationAPI.getStatus(mediaId);
        if (status.status === 'complete') {
          navigate(`/result/${mediaId}`);
          return;
        }
        if (status.status === 'failed') {
          setError('Verification failed.');
          setIsUploading(false);
          return;
        }
        setUploadProgress(status.progress);
        if (attempts < 30) {
          attempts++;
          setTimeout(poll, 2000);
        } else {
          setError('Taking longer than expected. Check back later.');
          setIsUploading(false);
        }
      } catch {
        if (attempts < 30) {
          attempts++;
          setTimeout(poll, 2000);
        }
      }
    };
    poll();
  };

  return (
    <div>
      {/* ═══════════ HERO ═══════════ */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid" />
        <div className="absolute -top-32 left-1/2 h-[420px] w-[720px] -translate-x-1/2 rounded-full bg-saffron-500/10 blur-[120px]" />

        <div className="relative mx-auto max-w-6xl px-4 pb-20 pt-16 sm:px-6 sm:pt-24">
          <div className="grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
            {/* Left: copy */}
            <div className="text-center lg:text-left">
              <div className="animate-fade-up inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-1.5 backdrop-blur-sm">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping-slow rounded-full bg-emerald-400" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
                </span>
                <span className="text-xs font-semibold tracking-wide text-slate-300">
                  {lang === 'hi' ? 'ओम्निकॉन हैकाथॉन 2026 · साइबरटेक' : 'Omnikon Hackathon 2026 · CyberTech'}
                </span>
              </div>

              <h1
                className="animate-fade-up mt-6 font-display text-4xl font-extrabold leading-[1.12] tracking-tight text-white sm:text-5xl xl:text-[3.6rem]"
                style={{ animationDelay: '80ms' }}
              >
                {lang === 'hi' ? (
                  <>
                    मीडिया की <span className="text-gradient">सच्चाई</span> जानें
                  </>
                ) : (
                  <>
                    Verify what&apos;s <span className="text-gradient">real.</span>
                    <br />
                    Expose what&apos;s not.
                  </>
                )}
              </h1>

              <p
                className="animate-fade-up mx-auto mt-5 max-w-lg text-base leading-relaxed text-slate-400 sm:text-lg lg:mx-0"
                style={{ animationDelay: '160ms' }}
              >
                {lang === 'hi'
                  ? 'AI से तस्वीरें, वीडियो और आवाज़ की जाँच करें — कुछ ही सेकंड में विश्वास स्कोर, स्पष्ट साक्ष्य और सही सलाह पाएं।'
                  : 'AI-powered deepfake detection for images, video & voice — an instant Trust Score, explainable evidence, and clear next steps.'}
              </p>

              <div className="animate-fade-up mt-8 flex flex-wrap items-center justify-center gap-3 lg:justify-start" style={{ animationDelay: '240ms' }}>
                <a href="#verify" className="btn-primary !px-7 !py-3 !text-base">
                  <Icon name="scanLine" className="h-5 w-5" />
                  {lang === 'hi' ? 'अभी जाँच करें' : 'Verify Now'}
                </a>
                <a href="#how-it-works" className="btn-outline !px-6 !py-3">
                  {lang === 'hi' ? 'यह कैसे काम करता है' : 'How it works'}
                  <Icon name="arrowRight" className="h-4 w-4" />
                </a>
              </div>

              {/* Stats */}
              <div className="animate-fade-up mt-12 grid grid-cols-3 divide-x divide-white/[0.07]" style={{ animationDelay: '320ms' }}>
                {[
                  { value: '500K+', labelHi: 'डीपफेक / माह', labelEn: 'Deepfakes / month' },
                  { value: '3×', labelHi: 'तेज़ फैलाव', labelEn: 'Faster misinformation spread' },
                  { value: '96%', labelHi: 'चेहरा हेरफेर', labelEn: 'Are face manipulations' },
                ].map((s, i) => (
                  <div key={i} className="px-4 text-center lg:first:pl-0 lg:text-left">
                    <p className="font-display text-2xl font-bold text-white sm:text-3xl">{s.value}</p>
                    <p className="mt-1 text-[11px] leading-snug text-slate-500">{lang === 'hi' ? s.labelHi : s.labelEn}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: floating preview */}
            <div className="relative mx-auto hidden w-full max-w-md lg:block" aria-hidden="true">
              {/* Main analysis card */}
              <div className="glass-card animate-float p-6 shadow-glow">
                <div className="flex items-center justify-between border-b border-white/[0.06] pb-4">
                  <div className="flex items-center gap-2.5">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-saffron-500/15">
                      <Icon name="shieldCheck" className="h-4 w-4 text-saffron-400" />
                    </span>
                    <p className="font-mono text-xs font-medium uppercase tracking-wider text-slate-400">Trust Analysis</p>
                  </div>
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-400/10 px-2.5 py-1 font-mono text-2xs font-semibold text-emerald-300">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                    COMPLETE
                  </span>
                </div>

                <MiniGauge score={92} />

                <div className="mt-5 space-y-2.5">
                  <SignalRow label="EfficientNet-B4" value={0.94} tone="emerald" />
                  <SignalRow label="XceptionNet" value={0.91} tone="emerald" />
                  <SignalRow label="Gemini Vision" value={0.88} tone="emerald" />
                  <SignalRow label="Threat Intel" value={0.97} tone="emerald" />
                </div>
              </div>

              {/* Secondary fusion card */}
              <div
                className="glass-card absolute -bottom-10 -left-10 w-56 animate-float p-4"
                style={{ animationDelay: '-3.2s' }}
              >
                <div className="flex items-center gap-2">
                  <Icon name="layers" className="h-4 w-4 text-violet-400" />
                  <p className="font-mono text-2xs font-semibold uppercase tracking-wider text-slate-400">Risk Fusion</p>
                </div>
                <div className="mt-3 flex items-end gap-1.5">
                  {[42, 58, 36, 74, 52, 88, 64, 46, 78, 92].map((h, i) => (
                    <span
                      key={i}
                      className="w-2.5 rounded-t bg-gradient-to-t from-violet-600/40 to-fuchsia-400"
                      style={{ height: `${h * 0.55}px` }}
                    />
                  ))}
                </div>
                <p className="mt-2.5 font-mono text-xs text-slate-500">
                  weighted · re-normalized
                </p>
              </div>

              {/* Glow behind cards */}
              <div className="absolute -inset-8 -z-10 rounded-[40px] bg-gradient-to-br from-saffron-500/[0.08] via-transparent to-violet-500/[0.08] blur-2xl" />
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ UPLOAD ═══════════ */}
      <section id="verify" className="mx-auto -mt-4 max-w-3xl scroll-mt-24 px-4 pb-20 sm:px-6">
        <div className="gradient-border rounded-2xl shadow-glow-lg">
          <div className="rounded-2xl p-6 sm:p-8">
            {isUploading ? (
              <AnalysisLoader progressText={uploadProgress} />
            ) : (
              <>
                {error && (
                  <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-400/25 bg-red-500/[0.07] p-4">
                    <Icon name="alertCircle" className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
                    <p className="text-sm text-red-300">{error}</p>
                  </div>
                )}
                <FileUpload onFileSelect={handleFileSelect} onLinkSubmit={handleLinkSubmit} isLoading={isUploading} />
              </>
            )}
          </div>
        </div>
      </section>

      {/* ═══════════ WHY ═══════════ */}
      <section className="mx-auto max-w-6xl px-4 pb-20 sm:px-6">
        <SectionHeading
          eyebrow={lang === 'hi' ? 'क्यों सत्यकवच' : 'Why SatyaKavach'}
          title={lang === 'hi' ? 'भरोसा, सिद्ध किया हुआ' : 'Trust, engineered in'}
        />
        <div className="grid gap-5 md:grid-cols-3">
          <FeatureCard
            icon="sparkles"
            titleHi="समझने योग्य AI"
            titleEn="Explainable AI"
            descHi="सिर्फ़ स्कोर नहीं — हर फ़ैसले के पीछे का साक्ष्य, कौन-से मॉडल ने क्या पाया, सब खुलकर।"
            descEn="Not just a score — every verdict ships with the evidence behind it and which models found what."
            tone="violet"
          />
          <FeatureCard
            icon="lock"
            titleHi="प्राइवेसी पहले"
            titleEn="Privacy First"
            descHi="मीडिया एन्क्रिप्टेड स्टोरेज में, न्यूनतम डेटा संग्रह, पूर्ण ऑडिट ट्रेल के साथ।"
            descEn="Encrypted storage, minimal data collection, and a full audit trail behind every analysis."
            tone="cyan"
          />
          <FeatureCard
            icon="globe"
            titleHi="हिंदी-प्रथम इंटरफ़ेस"
            titleEn="Hindi-First Interface"
            descHi="हर भारतीय नागरिक के लिए — सरल हिंदी में रिपोर्ट, एक टैप में I4C/1930 रिपोर्टिंग।"
            descEn="Built for every Indian citizen — reports in simple Hindi, one-tap I4C/1930 escalation."
            tone="saffron"
          />
        </div>
      </section>

      {/* ═══════════ HOW IT WORKS ═══════════ */}
      <section id="how-it-works" className="mx-auto max-w-6xl scroll-mt-24 px-4 pb-24 sm:px-6">
        <SectionHeading
          eyebrow={lang === 'hi' ? 'प्रक्रिया' : 'Process'}
          title={lang === 'hi' ? 'चार कदम, पूरी सच्चाई' : 'Four steps to the truth'}
        />

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {(
            [
              {
                step: '01',
                icon: 'uploadCloud' as IconName,
                titleHi: 'अपलोड करें',
                titleEn: 'Upload',
                descHi: 'तस्वीर, वीडियो, आवाज़ या लिंक',
                descEn: 'Image, video, audio or link',
                tone: 'from-sky-500/20 to-sky-500/[0.03] text-sky-300 border-sky-400/20',
              },
              {
                step: '02',
                icon: 'cpu' as IconName,
                titleHi: 'AI जाँच',
                titleEn: 'AI analysis',
                descHi: 'कई मॉडल समानांतर जाँच करते हैं',
                descEn: 'Multiple models run in parallel',
                tone: 'from-violet-500/20 to-violet-500/[0.03] text-violet-300 border-violet-400/20',
              },
              {
                step: '03',
                icon: 'target' as IconName,
                titleHi: 'ट्रस्ट स्कोर',
                titleEn: 'Trust Score',
                descHi: '0–100 स्कोर + स्पष्ट सिफ़ारिश',
                descEn: '0–100 score + clear recommendation',
                tone: 'from-saffron-500/20 to-saffron-500/[0.03] text-saffron-300 border-saffron-400/20',
              },
              {
                step: '04',
                icon: 'fileText' as IconName,
                titleHi: 'साक्ष्य रिपोर्ट',
                titleEn: 'Evidence report',
                descHi: 'हर फ़ैसले के पीछे पूरा सबूत',
                descEn: 'Full proof behind every verdict',
                tone: 'from-emerald-500/20 to-emerald-500/[0.03] text-emerald-300 border-emerald-400/20',
              },
            ] as const
          ).map((step, i) => (
            <div key={step.step} className="card-hover group relative p-6">
              {/* Connector (desktop) */}
              {i < 3 && (
                <div className="pointer-events-none absolute right-[-13px] top-11 z-10 hidden h-px w-[26px] bg-gradient-to-r from-white/15 to-white/5 lg:block" />
              )}

              <div className="flex items-center justify-between">
                <span className={`flex h-11 w-11 items-center justify-center rounded-xl border bg-gradient-to-br ${step.tone}`}>
                  <Icon name={step.icon} className="h-5 w-5" strokeWidth={1.6} />
                </span>
                <span className="font-display text-3xl font-extrabold text-white/[0.07] transition-colors duration-300 group-hover:text-white/[0.12]">
                  {step.step}
                </span>
              </div>
              <h3 className="font-display mt-4 text-base font-semibold text-white">
                {lang === 'hi' ? step.titleHi : step.titleEn}
              </h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-500">
                {lang === 'hi' ? step.descHi : step.descEn}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

/* ── Section heading ── */
function SectionHeading({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="mb-10 text-center">
      <p className="font-mono text-2xs font-semibold uppercase tracking-[0.28em] text-saffron-500">{eyebrow}</p>
      <h2 className="font-display mt-2 text-2xl font-bold text-white sm:text-3xl">{title}</h2>
    </div>
  );
}

/* ── Feature card ── */
function FeatureCard({
  icon,
  titleHi,
  titleEn,
  descHi,
  descEn,
  tone,
}: {
  icon: IconName;
  titleHi: string;
  titleEn: string;
  descHi: string;
  descEn: string;
  tone: 'violet' | 'cyan' | 'saffron';
}) {
  const { lang } = useLang();
  const tones = {
    violet: 'border-violet-400/20 bg-violet-400/[0.08] text-violet-300',
    cyan: 'border-cyan-400/20 bg-cyan-400/[0.08] text-cyan-300',
    saffron: 'border-saffron-400/20 bg-saffron-400/[0.08] text-saffron-300',
  };
  return (
    <div className="card-hover p-6">
      <span className={`inline-flex h-12 w-12 items-center justify-center rounded-xl border ${tones[tone]}`}>
        <Icon name={icon} className="h-5 w-5" strokeWidth={1.6} />
      </span>
      <h3 className="font-display mt-4 text-lg font-semibold text-white">
        {lang === 'hi' ? titleHi : titleEn}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-500">{lang === 'hi' ? descHi : descEn}</p>
    </div>
  );
}

/* ── Mini gauge used in hero preview ── */
function MiniGauge({ score }: { score: number }) {
  const size = 150;
  const sw = 10;
  const r = size / 2 - sw;
  const C = 2 * Math.PI * r;
  const ARC = C * 0.75;

  return (
    <div className="relative mx-auto mt-4" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="miniGrad" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#34D399" />
            <stop offset="100%" stopColor="#10B981" />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={sw}
          strokeLinecap="round"
          strokeDasharray={`${ARC} ${C}`}
          transform={`rotate(135 ${size / 2} ${size / 2})`}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="url(#miniGrad)"
          strokeWidth={sw}
          strokeLinecap="round"
          strokeDasharray={`${(score / 100) * ARC} ${C}`}
          transform={`rotate(135 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center pb-1.5">
        <span className="font-display text-4xl font-bold tabular-nums text-emerald-300">{score}</span>
        <span className="mt-0.5 text-[9px] font-semibold uppercase tracking-[0.22em] text-slate-500">High Trust</span>
      </div>
    </div>
  );
}

function SignalRow({ label, value, tone }: { label: string; value: number; tone: 'emerald' }) {
  return (
    <div>
      <div className="flex items-center justify-between text-2xs">
        <span className="font-mono text-slate-500">{label}</span>
        <span className="font-mono font-semibold text-emerald-300">{Math.round(value * 100)}%</span>
      </div>
      <div className="mt-1 h-1 overflow-hidden rounded-full bg-white/[0.05]">
        <div
          className={`h-full rounded-full ${
            tone === 'emerald' ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : ''
          }`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
    </div>
  );
}

/* ── Analysis loading state ── */
const PIPELINE_STEPS = [
  { key: 'pre', labelHi: 'मीडिया तैयार हो रहा है', labelEn: 'Preprocessing media', icon: 'layers' as IconName },
  { key: 'ai', labelHi: 'AI मॉडल जाँच रहे हैं', labelEn: 'AI models analyzing', icon: 'cpu' as IconName },
  { key: 'risk', labelHi: 'रिस्क इंजन स्कोर बना रहा है', labelEn: 'Fusing trust signals', icon: 'activity' as IconName },
  { key: 'report', labelHi: 'रिपोर्ट तैयार हो रही है', labelEn: 'Generating evidence report', icon: 'fileText' as IconName },
];

function AnalysisLoader({ progressText }: { progressText: string }) {
  const [activeStep, setActiveStep] = useState(0);
  const { lang } = useLang();

  useEffect(() => {
    const id = setInterval(() => setActiveStep((s) => (s + 1) % PIPELINE_STEPS.length), 1800);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="py-6">
      {/* Scanner visual */}
      <div className="relative mx-auto h-44 max-w-md overflow-hidden rounded-xl border border-white/[0.07] bg-ink-900/60">
        {/* Fake frame grid */}
        <div className="absolute inset-0 opacity-60">
          {Array.from({ length: 6 }).map((_, r) =>
            Array.from({ length: 8 }).map((_, c) => (
              <div
                key={`${r}-${c}`}
                className="absolute border border-emerald-400/[0.06]"
                style={{
                  left: `${c * 12.5}%`,
                  top: `${r * 16.66}%`,
                  width: '12.5%',
                  height: '16.66%',
                }}
              />
            )),
          )}
        </div>
        {/* Corner brackets */}
        {['top-3 left-3 border-t-2 border-l-2', 'top-3 right-3 border-t-2 border-r-2', 'bottom-3 left-3 border-b-2 border-l-2', 'bottom-3 right-3 border-b-2 border-r-2'].map(
          (pos, i) => (
            <span key={i} className={`absolute h-5 w-5 rounded-sm border-emerald-400/70 ${pos}`} />
          ),
        )}
        {/* Scan line */}
        <div className="scan-line absolute left-0 h-16 w-full animate-scan opacity-80" />
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 rounded-md bg-black/50 px-3 py-1 font-mono text-2xs text-emerald-300 backdrop-blur-sm">
          SCANNING · MULTIMODAL ANALYSIS
        </div>
      </div>

      {/* Pipeline steps */}
      <div className="mt-8 space-y-2.5">
        {PIPELINE_STEPS.map((step, i) => {
          const isActive = i === activeStep;
          const isDone = i < activeStep;
          return (
            <div
              key={step.key}
              className={`flex items-center gap-3 rounded-xl border px-4 py-3 transition-all duration-500 ${
                isActive
                  ? 'border-saffron-500/30 bg-saffron-500/[0.06]'
                  : isDone
                    ? 'border-emerald-400/20 bg-emerald-400/[0.04]'
                    : 'border-transparent bg-white/[0.02] opacity-50'
              }`}
            >
              {isActive ? (
                <span className="flex h-5 w-5 shrink-0 items-center justify-center">
                  <span className="h-4 w-4 animate-spin-slow rounded-full border-2 border-saffron-400 border-t-transparent" />
                </span>
              ) : isDone ? (
                <Icon name="checkCircle" className="h-5 w-5 shrink-0 text-emerald-400" />
              ) : (
                <span className="h-5 w-5 shrink-0 rounded-full border border-white/15" />
              )}
              <p className={`text-sm font-medium ${isActive ? 'text-white' : isDone ? 'text-emerald-200/80' : 'text-slate-500'}`}>
                {lang === 'hi' ? step.labelHi : step.labelEn}
              </p>
            </div>
          );
        })}
      </div>

      <p className="mt-6 text-center font-mono text-xs text-slate-500">{progressText}</p>
    </div>
  );
}
