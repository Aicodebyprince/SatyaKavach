/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Deep-space background scale
        ink: {
          950: "#05070D",
          900: "#080C16",
          850: "#0B1120",
          800: "#0F1628",
          700: "#16203A",
          600: "#1E2B4D",
        },
        // Brand primary — refined saffron
        saffron: {
          50: "#FFF8F0",
          100: "#FFEEDA",
          200: "#FFDBAE",
          300: "#FCBE77",
          400: "#FB9E3E",
          500: "#F97316",
          600: "#E85D04",
          700: "#C2470A",
          800: "#9A3A0F",
        },
        // Legacy aliases kept for compatibility
        navy: {
          50: "#F0F4FF",
          100: "#DCE6FF",
          200: "#B4C6FB",
          300: "#7E99F5",
          400: "#5472EE",
          500: "#2F51E4",
          600: "#2340C7",
          700: "#1B3195",
          800: "#131F52",
          900: "#0B1120",
        },
        trust: {
          high: "#34D399",
          uncertain: "#FBBF24",
          low: "#F87171",
        },
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans Devanagari", "system-ui", "sans-serif"],
        display: ["Sora", "Noto Sans Devanagari", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem" }],
      },
      boxShadow: {
        glow: "0 0 40px -12px rgba(249, 115, 22, 0.45)",
        "glow-lg": "0 0 80px -20px rgba(249, 115, 22, 0.5)",
        "glow-green": "0 0 40px -12px rgba(52, 211, 153, 0.45)",
        "glow-red": "0 0 40px -12px rgba(248, 113, 113, 0.5)",
        "glow-amber": "0 0 40px -12px rgba(251, 191, 36, 0.45)",
        card: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 20px 50px -30px rgba(0,0,0,0.7)",
      },
      backgroundImage: {
        "grid-faint":
          "linear-gradient(rgba(148,163,184,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.05) 1px, transparent 1px)",
      },
      animation: {
        "fade-up": "fadeUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) both",
        "fade-in": "fadeIn 0.5s ease-out both",
        float: "float 7s ease-in-out infinite",
        "spin-slow": "spin 2.4s linear infinite",
        shimmer: "shimmer 2.2s linear infinite",
        scan: "scan 2.4s ease-in-out infinite",
        "pulse-glow": "pulseGlow 2.6s ease-in-out infinite",
        "ping-slow": "pingSlow 2.2s cubic-bezier(0, 0, 0.2, 1) infinite",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(18px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-14px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        scan: {
          "0%, 100%": { transform: "translateY(-120%)" },
          "50%": { transform: "translateY(120%)" },
        },
        pulseGlow: {
          "0%, 100%": { filter: "drop-shadow(0 0 6px currentColor)" },
          "50%": { filter: "drop-shadow(0 0 18px currentColor)" },
        },
        pingSlow: {
          "75%, 100%": { transform: "scale(2)", opacity: "0" },
        },
      },
    },
  },
  plugins: [],
};
