import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLang } from '../App';
import { t } from '../i18n/translations';
import Icon, { type IconName } from '../components/Icon';
import MiniRing from '../components/MiniRing';
import { verificationAPI } from '../services/api';
import type { TrustScoreResult } from '../types';

const MEDIA_META: Record<string, { icon: IconName; cls: string }> = {
  image: { icon: 'image', cls: 'border-sky-400/25 bg-sky-400/[0.08] text-sky-300' },
  video: { icon: 'video', cls: 'border-violet-400/25 bg-violet-400/[0.08] text-violet-300' },
  audio: { icon: 'mic', cls: 'border-emerald-400/25 bg-emerald-400/[0.08] text-emerald-300' },
  link: { icon: 'link', cls: 'border-amber-400/25 bg-amber-400/[0.08] text-amber-300' },
};

export default function HistoryPage() {
  const { lang } = useLang();
  const navigate = useNavigate();
  const [records, setRecords] = useState<TrustScoreResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  useEffect(() => {
    loadHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  const loadHistory = async () => {
    try {
      const data = await verificationAPI.getHistory(page);
      setRecords(data.records);
      setTotal(data.total);
    } catch {
      // User might not be authenticated
      console.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl space-y-3 px-4 py-10 sm:px-6">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="skeleton h-[76px] w-full !rounded-xl" />
        ))}
      </div>
    );
  }

  if (records.length === 0) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <div className="glass-card max-w-sm space-y-4 p-10 text-center">
          <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03]">
            <Icon name="history" className="h-7 w-7 text-slate-500" strokeWidth={1.5} />
          </span>
          <p className="text-slate-400">
            {lang === 'hi' ? 'अभी तक कोई जाँच नहीं हुई' : 'No verifications yet'}
          </p>
          <button onClick={() => navigate('/')} className="btn-primary mx-auto">
            <Icon name="uploadCloud" className="h-4 w-4" />
            {t('uploadNew', lang)}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="font-mono text-2xs font-semibold uppercase tracking-[0.28em] text-saffron-500">
            {lang === 'hi' ? 'इतिहास' : 'History'}
          </p>
          <h1 className="font-display mt-1 text-2xl font-bold text-white sm:text-3xl">
            {lang === 'hi' ? 'जाँच इतिहास' : 'Verification history'}
          </h1>
        </div>
        <span className="rounded-full border border-white/10 bg-white/[0.04] px-3.5 py-1.5 font-mono text-xs font-semibold text-slate-400 tabular-nums">
          {total} {lang === 'hi' ? 'रिकॉर्ड' : total === 1 ? 'record' : 'records'}
        </span>
      </div>

      {/* Records */}
      <div className="space-y-2.5">
        {records.map((record, i) => {
          const meta = MEDIA_META[record.media_type] ?? MEDIA_META.image;
          return (
            <button
              key={record.record_id}
              onClick={() => navigate(`/result/${record.media_id}`)}
              className="card-hover group flex w-full animate-fade-up items-center gap-4 p-4 text-left"
              style={{ animationDelay: `${Math.min(i * 40, 240)}ms` }}
            >
              {/* Score ring */}
              <MiniRing score={record.trust_score} verdict={record.verdict} size={56} />

              {/* Type tile */}
              <span
                className={`hidden h-11 w-11 shrink-0 items-center justify-center rounded-xl border sm:flex ${meta.cls}`}
              >
                <Icon name={meta.icon} className="h-5 w-5" strokeWidth={1.6} />
              </span>

              {/* Details */}
              <div className="min-w-0 flex-1">
                <p className="truncate font-display text-sm font-semibold capitalize text-white">
                  {record.media_type}
                  <span className="ml-2 font-mono text-xs font-normal normal-case text-slate-500">
                    {new Date(record.created_at).toLocaleDateString(lang === 'hi' ? 'hi-IN' : 'en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </p>
                <p
                  className={`mt-0.5 inline-flex items-center gap-1.5 text-xs font-medium ${
                    record.verdict === 'HIGH_TRUST'
                      ? 'text-emerald-300'
                      : record.verdict === 'UNCERTAIN'
                        ? 'text-amber-300'
                        : 'text-red-300'
                  }`}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      record.verdict === 'HIGH_TRUST'
                        ? 'bg-emerald-400'
                        : record.verdict === 'UNCERTAIN'
                          ? 'bg-amber-400'
                          : 'bg-red-400'
                    }`}
                  />
                  {record.verdict === 'HIGH_TRUST'
                    ? t('highTrust', lang)
                    : record.verdict === 'UNCERTAIN'
                      ? t('uncertain', lang)
                      : t('lowTrust', lang)}
                </p>
              </div>

              <Icon
                name="chevronRight"
                className="h-5 w-5 shrink-0 text-slate-600 transition-all duration-200 group-hover:translate-x-1 group-hover:text-saffron-400"
              />
            </button>
          );
        })}
      </div>

      {/* Pagination */}
      {total > 20 && (
        <div className="mt-8 flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-outline !px-4 text-sm disabled:opacity-40"
          >
            <Icon name="arrowLeft" className="h-4 w-4" />
            {lang === 'hi' ? 'पिछला' : 'Prev'}
          </button>
          <span className="px-4 py-2 font-mono text-sm text-slate-500 tabular-nums">{page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={records.length < 20}
            className="btn-outline !px-4 text-sm disabled:opacity-40"
          >
            {lang === 'hi' ? 'अगला' : 'Next'}
            <Icon name="arrowRight" className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
