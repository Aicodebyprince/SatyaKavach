import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useLang } from '../App';
import { t } from '../i18n/translations';
import TrustGauge from '../components/TrustGauge';
import Icon, { type IconName } from '../components/Icon';
import { verificationAPI } from '../services/api';
import type { TrustScoreResult } from '../types';

const MEDIA_ICONS: Record<string, { icon: IconName; tone: string }> = {
  image: { icon: 'image', tone: 'border-sky-400/25 bg-sky-400/[0.08] text-sky-300' },
  video: { icon: 'video', tone: 'border-violet-400/25 bg-violet-400/[0.08] text-violet-300' },
  audio: { icon: 'mic', tone: 'border-emerald-400/25 bg-emerald-400/[0.08] text-emerald-300' },
  link: { icon: 'link', tone: 'border-amber-400/25 bg-amber-400/[0.08] text-amber-300' },
};

export default function ResultsPage() {
  const { mediaId } = useParams<{ mediaId: string }>();
  const { lang } = useLang();
  const navigate = useNavigate();
  const [result, setResult] = useState<TrustScoreResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!mediaId) return;
    loadResult(mediaId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mediaId]);

  const loadResult = async (id: string) => {
    try {
      const data = await verificationAPI.getResult(id);
      setResult(data);
    } catch (err: any) {
      if (err.response?.status === 202) {
        setTimeout(() => loadResult(id), 2000);
        return;
      }
      setError(err.response?.data?.detail || 'Failed to load result');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="space-y-4 text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-[3px] border-saffron-500 border-t-transparent" />
          <p className="font-mono text-sm text-slate-400">{t('analyzing', lang)}</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <div className="glass-card space-y-4 p-10 text-center">
          <Icon name="alertCircle" className="mx-auto h-12 w-12 text-red-400" strokeWidth={1.5} />
          <p className="text-red-300">{error || 'Result not found'}</p>
          <button onClick={() => navigate('/')} className="btn-primary mx-auto">
            {t('uploadNew', lang)}
          </button>
        </div>
      </div>
    );
  }

  const report = result.evidence_report;
  const mediaMeta = MEDIA_ICONS[result.media_type] ?? MEDIA_ICONS.image;

  return (
    <div className="mx-auto max-w-5xl space-y-6 px-4 py-10 sm:px-6">
      {/* Back */}
      <button onClick={() => navigate('/')} className="btn-ghost -mb-2 !pl-2">
        <Icon name="arrowLeft" className="h-4 w-4" />
        {lang === 'hi' ? 'नई जाँच' : 'New verification'}
      </button>

      {/* ═══ Verdict panel ═══ */}
      <section className="gradient-border animate-fade-up rounded-2xl">
        <div className="grid gap-8 rounded-2xl p-6 sm:p-10 lg:grid-cols-[auto_1fr] lg:items-center">
          <div className="mx-auto">
            <TrustGauge score={result.trust_score} verdict={result.verdict} size={250} />
          </div>

          <div className="text-center lg:text-left">
            {/* Meta chips */}
            <div className="flex flex-wrap items-center justify-center gap-2 lg:justify-start">
              <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-mono text-2xs font-semibold uppercase tracking-wider ${mediaMeta.tone}`}>
                <Icon name={mediaMeta.icon} className="h-3.5 w-3.5" />
                {result.media_type}
              </span>
              {result.analysis_duration_ms && (
                <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 font-mono text-2xs text-slate-400">
                  <Icon name="clock" className="h-3.5 w-3.5" />
                  {(result.analysis_duration_ms / 1000).toFixed(1)}s
                </span>
              )}
              <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 font-mono text-2xs text-slate-400">
                <Icon name="checkCircle" className="h-3.5 w-3.5 text-emerald-400" />
                {report.analysis_completeness}
              </span>
            </div>

            <h1 className="font-display mt-5 text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              {t('analysisComplete', lang)}
            </h1>
            <p className="mt-3 leading-relaxed text-slate-400">
              {lang === 'hi' ? report.summary_hi : report.summary_en}
            </p>

            {/* Signals analyzed */}
            {report.signals_analyzed?.length > 0 && (
              <div className="mt-5 flex flex-wrap justify-center gap-1.5 lg:justify-start">
                {report.signals_analyzed.map((sig) => (
                  <span key={sig} className="rounded-md border border-white/[0.07] bg-white/[0.03] px-2 py-1 font-mono text-2xs text-slate-500">
                    {sig}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* ═══ Findings ═══ */}
      {report.findings && report.findings.length > 0 && (
        <section className="glass-card animate-fade-up p-6 sm:p-8" style={{ animationDelay: '80ms' }}>
          <CardHeader icon="search" title={t('evidenceReport', lang)} />

          <div className="space-y-3">
            {report.findings.map((finding, i) => {
              const tone =
                finding.severity === 'high'
                  ? { icon: 'alertTriangle' as IconName, cls: 'border-red-400/25 bg-red-500/[0.06]', iconCls: 'bg-red-500/15 text-red-400' }
                  : finding.severity === 'medium'
                    ? { icon: 'info' as IconName, cls: 'border-amber-400/25 bg-amber-400/[0.05]', iconCls: 'bg-amber-400/15 text-amber-400' }
                    : { icon: 'shieldCheck' as IconName, cls: 'border-emerald-400/25 bg-emerald-400/[0.05]', iconCls: 'bg-emerald-400/15 text-emerald-400' };
              return (
                <div key={i} className={`flex items-start gap-4 rounded-xl border p-4 ${tone.cls}`}>
                  <span className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${tone.iconCls}`}>
                    <Icon name={tone.icon} className="h-4.5 w-4.5 h-[18px] w-[18px]" strokeWidth={1.9} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300">
                      {finding.signal}
                      <span className={`ml-2 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                        finding.severity === 'high'
                          ? 'bg-red-500/20 text-red-300'
                          : finding.severity === 'medium'
                            ? 'bg-amber-400/20 text-amber-300'
                            : 'bg-emerald-400/20 text-emerald-300'
                      }`}>
                        {finding.severity}
                      </span>
                    </p>
                    <p className="mt-1.5 text-sm leading-relaxed text-slate-400">{finding.message}</p>
                    {finding.models && finding.models.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {finding.models.map((m) => (
                          <span key={m} className="rounded border border-white/[0.07] bg-black/30 px-1.5 py-0.5 font-mono text-2xs text-slate-500">
                            {m}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* ═══ Model breakdown ═══ */}
      <section className="glass-card animate-fade-up p-6 sm:p-8" style={{ animationDelay: '140ms' }}>
        <CardHeader icon="cpu" title={t('modelBreakdown', lang)} />
        <ModelBreakdown breakdown={result.model_breakdown} />
      </section>

      {/* ═══ Artifacts ═══ */}
      {report.artifacts && report.artifacts.length > 0 && (
        <section className="glass-card animate-fade-up p-6 sm:p-8" style={{ animationDelay: '200ms' }}>
          <CardHeader
            icon="fileText"
            title={lang === 'hi' ? 'पाए गए आर्टिफैक्ट' : 'Detected artifacts'}
          />
          <div className="flex flex-wrap gap-2">
            {report.artifacts.map((a, i) => (
              <span
                key={i}
                className="inline-flex max-w-full items-center gap-1.5 rounded-lg border border-saffron-500/20 bg-saffron-500/[0.06] px-3 py-1.5 font-mono text-xs text-saffron-200/90"
              >
                <span className="h-1 w-1 shrink-0 rounded-full bg-saffron-400" />
                <span className="truncate">{a}</span>
              </span>
            ))}
          </div>
        </section>
      )}

      {/* ═══ Recommended action ═══ */}
      <section className="gradient-border animate-fade-up rounded-2xl shadow-glow" style={{ animationDelay: '260ms' }}>
        <div className="rounded-2xl p-6 sm:p-8">
          <div className="flex items-start gap-4">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-saffron-500/15 text-saffron-400">
              <Icon name="target" className="h-5 w-5" />
            </span>
            <div className="min-w-0">
              <h3 className="font-display text-lg font-bold text-white">{t('recommendedAction', lang)}</h3>
              <p className="mt-1.5 leading-relaxed text-slate-300">{result.recommended_action}</p>

              {result.verdict === 'LOW_TRUST' && (
                <button className="btn-secondary mt-5">
                  <Icon name="flag" className="h-4 w-4" />
                  {t('reportToI4C', lang)}
                </button>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Bottom actions ═══ */}
      <div className="flex flex-wrap justify-center gap-3 pb-8 pt-2">
        <button onClick={() => navigate('/')} className="btn-primary">
          <Icon name="uploadCloud" className="h-4 w-4" />
          {t('uploadNew', lang)}
        </button>
        <button className="btn-outline">
          <Icon name="share2" className="h-4 w-4" />
          {t('shareResult', lang)}
        </button>
      </div>
    </div>
  );
}

/* ── Section header inside cards ── */
function CardHeader({ icon, title }: { icon: IconName; title: string }) {
  return (
    <div className="mb-5 flex items-center gap-3">
      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/[0.04] text-saffron-400">
        <Icon name={icon} className="h-4.5 w-4.5 h-[18px] w-[18px]" />
      </span>
      <h3 className="font-display text-base font-bold text-white sm:text-lg">{title}</h3>
    </div>
  );
}

/* ── Generic model breakdown renderer ── */
function ModelBreakdown({ breakdown }: { breakdown: Record<string, any> }) {
  const groups = Object.entries(breakdown).filter(
    ([key, value]) => key !== 'signal_weights' && key !== 'available_signals' && typeof value === 'object' && value !== null,
  );

  if (groups.length === 0) {
    return <p className="text-sm text-slate-500">No model data available.</p>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {groups.map(([group, values]) => (
        <div key={group} className="rounded-xl border border-white/[0.06] bg-ink-900/50 p-5">
          <p className="font-mono text-xs font-bold uppercase tracking-[0.18em] text-slate-400">{group}</p>
          <div className="mt-4 space-y-3">
            {Object.entries(values as Record<string, any>).map(([k, v]) =>
              typeof v === 'number' ? (
                <Bar key={k} label={k} value={v} />
              ) : (
                <div key={k} className="flex items-baseline justify-between gap-3 text-xs">
                  <span className="truncate font-mono text-slate-500">{humanize(k)}</span>
                  <span className="shrink-0 font-mono font-medium text-slate-300">{String(v)}</span>
                </div>
              ),
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function Bar({ label, value }: { label: string; value: number }) {
  // Scores may be 0..1 or 0..100 — normalize
  const pct = Math.max(0, Math.min(100, value <= 1 ? value * 100 : value));
  const tone =
    pct >= 70 ? 'from-emerald-500 to-teal-400' : pct >= 40 ? 'from-amber-400 to-orange-400' : 'from-red-400 to-rose-500';

  return (
    <div>
      <div className="flex items-baseline justify-between gap-3 text-xs">
        <span className="truncate font-mono text-slate-500">{humanize(label)}</span>
        <span className="shrink-0 font-mono font-semibold text-slate-200 tabular-nums">
          {value <= 1 ? value.toFixed(3) : Math.round(value)}
        </span>
      </div>
      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${tone}`}
          style={{ width: `${pct}%`, transition: 'width 1s cubic-bezier(0.22,1,0.36,1)' }}
        />
      </div>
    </div>
  );
}

function humanize(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
