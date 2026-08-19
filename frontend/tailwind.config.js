/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        chelsea: {
          blue: "#034694",
          gold: "#DBA111",
          red: "#ED1C24",
          navy: "#061428",
          ink: "#0B1D36",
        },
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
      },
      fontFamily: {
        sans: ["Manrope", "ui-sans-serif", "system-ui"],
        display: ["Fraunces", "ui-serif", "Georgia"],
      },
      boxShadow: {
        gold: "0 0 0 1px rgba(219, 161, 17, 0.35), 0 18px 50px rgba(3, 70, 148, 0.25)",
      },
    },
  },
  plugins: [],
};
