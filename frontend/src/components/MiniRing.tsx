interface MiniRingProps {
  score: number;
  verdict: 'HIGH_TRUST' | 'UNCERTAIN' | 'LOW_TRUST';
  size?: number;
}

const COLORS = {
  HIGH_TRUST: '#34D399',
  UNCERTAIN: '#FBBF24',
  LOW_TRUST: '#F87171',
};

export default function MiniRing({ score, verdict, size = 56 }: MiniRingProps) {
  const sw = 4.5;
  const r = size / 2 - sw / 2 - 1;
  const C = 2 * Math.PI * r;
  const ARC = C * 0.75;
  const color = COLORS[verdict];

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.07)"
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
          stroke={color}
          strokeWidth={sw}
          strokeLinecap="round"
          strokeDasharray={`${(score / 100) * ARC} ${C}`}
          transform={`rotate(135 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="font-display font-bold tabular-nums" style={{ fontSize: size * 0.28, color }}>
          {score}
        </span>
      </div>
    </div>
  );
}
