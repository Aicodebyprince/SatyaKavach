import { useEffect, useRef, useState } from 'react';
import Icon, { type IconName } from './Icon';

interface TrustGaugeProps {
  score: number;
  verdict: 'HIGH_TRUST' | 'UNCERTAIN' | 'LOW_TRUST';
  size?: number;
  showLabel?: boolean;
}

const VERDICT_CONFIG: Record<
  TrustGaugeProps['verdict'],
  {
    from: string;
    to: string;
    glowColor: string;
    labelHi: string;
    labelEn: string;
    icon: IconName;
    chipBg: string;
    chipText: string;
    shadowClass: string;
  }
> = {
  HIGH_TRUST: {
    from: '#34D399',
    to: '#10B981',
    glowColor: '#34D399',
    labelHi: 'विश्वसनीय',
    labelEn: 'Trustworthy',
    icon: 'shieldCheck',
    chipBg: 'bg-emerald-400/10 border-emerald-400/30',
    chipText: 'text-emerald-300',
    shadowClass: 'shadow-glow-green',
  },
  UNCERTAIN: {
    from: '#FBBF24',
    to: '#F59E0B',
    glowColor: '#FBBF24',
    labelHi: 'अनिश्चित',
    labelEn: 'Uncertain',
    icon: 'alertTriangle',
    chipBg: 'bg-amber-400/10 border-amber-400/30',
    chipText: 'text-amber-300',
    shadowClass: 'shadow-glow-amber',
  },
  LOW_TRUST: {
    from: '#F87171',
    to: '#EF4444',
    glowColor: '#F87171',
    labelHi: 'अविश्वसनीय',
    labelEn: 'Untrustworthy',
    icon: 'xCircle',
    chipBg: 'bg-red-400/10 border-red-400/30',
    chipText: 'text-red-300',
    shadowClass: 'shadow-glow-red',
  },
};

/** Animated count-up hook */
function useCountUp(target: number, duration = 1400) {
  const [value, setValue] = useState(0);
  const raf = useRef<number>();

  useEffect(() => {
    const start = performance.now();
    const from = 0;
    const tick = (now: number) => {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 4); // easeOutQuart
      setValue(Math.round(from + (target - from) * eased));
      if (p < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current!);
  }, [target, duration]);

  return value;
}

export default function TrustGauge({
  score,
  verdict,
  size = 240,
  showLabel = true,
}: TrustGaugeProps) {
  const config = VERDICT_CONFIG[verdict];
  const animatedScore = useCountUp(score);

  const strokeWidth = 13;
  const radius = size / 2 - strokeWidth / 2 - 6; // padding for ticks
  const cx = size / 2;
  const cy = size / 2;

  // 270° arc → 75% of circumference
  const C = 2 * Math.PI * radius;
  const ARC = C * 0.75;
  const progress = (animatedScore / 100) * ARC;

  const uid = `tg-${verdict}-${size}`;

  // Tick marks along the arc
  const ticks = Array.from({ length: 21 }, (_, i) => {
    const angleDeg = -225 + i * (270 / 20); // start at -225° going clockwise
    const rad = (angleDeg * Math.PI) / 180;
    const inner = radius + strokeWidth / 2 + 2;
    const outer = inner + (i % 5 === 0 ? 6 : 3);
    return {
      x1: cx + inner * Math.cos(rad),
      y1: cy + inner * Math.sin(rad),
      x2: cx + outer * Math.cos(rad),
      y2: cy + outer * Math.sin(rad),
      major: i % 5 === 0,
    };
  });

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={`Trust score ${score}`}>
          <defs>
            <linearGradient id={`${uid}-stroke`} x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={config.from} />
              <stop offset="100%" stopColor={config.to} />
            </linearGradient>
            <filter id={`${uid}-glow`} x="-40%" y="-40%" width="180%" height="180%">
              <feGaussianBlur stdDeviation="5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Ticks */}
          {ticks.map((t, i) => (
            <line
              key={i}
              x1={t.x1}
              y1={t.y1}
              x2={t.x2}
              y2={t.y2}
              stroke="#334155"
              strokeOpacity={t.major ? 0.8 : 0.35}
              strokeWidth={t.major ? 2 : 1}
              strokeLinecap="round"
            />
          ))}

          {/* Track */}
          <circle
            cx={cx}
            cy={cy}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={`${ARC} ${C}`}
            transform={`rotate(135 ${cx} ${cy})`}
          />

          {/* Progress */}
          <circle
            cx={cx}
            cy={cy}
            r={radius}
            fill="none"
            stroke={`url(#${uid}-stroke)`}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={`${progress} ${C}`}
            transform={`rotate(135 ${cx} ${cy})`}
            filter={`url(#${uid}-glow)`}
            style={{ transition: 'stroke-dasharray 0.12s linear' }}
          />
        </svg>

        {/* Center readout */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pb-2">
          <span
            className="font-display text-[52px] font-bold leading-none tabular-nums"
            style={{ color: config.glowColor }}
          >
            {animatedScore}
          </span>
          <span className="mt-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">
            / 100
          </span>
        </div>
      </div>

      {/* Verdict chip */}
      {showLabel && (
        <div
          className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold ${config.chipBg} ${config.chipText} ${config.shadowClass}`}
        >
          <Icon name={config.icon} className="h-4 w-4" strokeWidth={2} />
          {VERDICT_LABEL(verdict)}
        </div>
      )}
    </div>
  );

  function VERDICT_LABEL(v: TrustGaugeProps['verdict']) {
    const c = VERDICT_CONFIG[v];
    return (
      <span>
        {c.labelHi}
        <span className="mx-1.5 opacity-40">·</span>
        <span className="text-xs font-medium opacity-80">{c.labelEn}</span>
      </span>
    );
  }
}
