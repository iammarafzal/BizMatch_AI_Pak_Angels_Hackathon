import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC", // slate-50
        navy: {
          900: "#0F172A", // slate-900 / dark executive navy
          950: "#020617", // slate-950
        },
        brand: {
          50: "#EEF2FF",
          100: "#E0E7FF",
          200: "#C7D2FE",
          500: "#6366F1",
          600: "#4F46E5", // Primary executive indigo
          700: "#4338CA",
          800: "#3730A3",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          muted: "#F8FAFC",
          card: "#FFFFFF",
          border: "#E2E8F0",
        },
        fit: {
          high: {
            text: "#047857", // emerald-700
            bg: "#ECFDF5",    // emerald-50
            border: "#A7F3D0",// emerald-200
          },
          medium: {
            text: "#B45309", // amber-700
            bg: "#FFFBEB",    // amber-50
            border: "#FDE68A",// amber-200
          },
          low: {
            text: "#334155", // slate-700
            bg: "#F1F5F9",    // slate-100
            border: "#E2E8F0",// slate-200
          },
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        subtle: "0 1px 2px 0 rgba(15, 23, 42, 0.05)",
        card: "0 1px 3px 0 rgba(15, 23, 42, 0.06), 0 1px 2px -1px rgba(15, 23, 42, 0.04)",
        "card-hover": "0 10px 15px -3px rgba(15, 23, 42, 0.07), 0 4px 6px -4px rgba(15, 23, 42, 0.04)",
        drawer: "-4px 0 24px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
