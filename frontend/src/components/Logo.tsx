/** SatyaKavach brand mark — gradient shield with check */
export default function Logo({
  className = 'w-9 h-9',
  id = 'logoGrad',
}: {
  className?: string;
  id?: string;
}) {
  return (
    <svg viewBox="0 0 40 40" fill="none" className={className} aria-hidden="true">
      <defs>
        <linearGradient id={id} x1="6" y1="4" x2="34" y2="36" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FB9E3E" />
          <stop offset="0.55" stopColor="#F97316" />
          <stop offset="1" stopColor="#DC5504" />
        </linearGradient>
        <linearGradient id={`${id}-shine`} x1="12" y1="6" x2="26" y2="30" gradientUnits="userSpaceOnUse">
          <stop stopColor="#fff" stopOpacity="0.35" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
      </defs>
      {/* Shield */}
      <path
        d="M20 3.5 33.5 9v8.2c0 8.6-5.6 14.6-13.5 17.8C12.1 31.8 6.5 25.8 6.5 17.2V9L20 3.5Z"
        fill={`url(#${id})`}
      />
      <path
        d="M20 3.5 33.5 9v8.2c0 8.6-5.6 14.6-13.5 17.8C12.1 31.8 6.5 25.8 6.5 17.2V9L20 3.5Z"
        fill={`url(#${id}-shine)`}
      />
      <path
        d="M20 3.5 33.5 9v8.2c0 8.6-5.6 14.6-13.5 17.8C12.1 31.8 6.5 25.8 6.5 17.2V9L20 3.5Z"
        stroke="#FFD9AE"
        strokeOpacity="0.5"
        strokeWidth="1.2"
      />
      {/* Check */}
      <path
        d="m13.5 19.5 4.4 4.4 8.6-8.6"
        stroke="#fff"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
