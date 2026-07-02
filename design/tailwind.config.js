/**
 * incident-retro "The Debrief" — Tailwind consumption of tokens.css
 * Tokens are CSS custom properties (theme via html[data-theme]).
 */
module.exports = {
  content: ["./docs/**/*.html", "./src/**/*.{js,jsx,ts,tsx,vue}"],
  darkMode: ["selector", '[data-theme="late-hour"]'],
  theme: {
    fontFamily: {
      display: ["Instrument Serif", "Georgia", "serif"],
      sans: ["Switzer", "system-ui", "sans-serif"],
      mono: ["Space Mono", "ui-monospace", "monospace"],
    },
    extend: {
      colors: {
        clay: { DEFAULT: "var(--bg)", card: "var(--surface)", inset: "var(--inset)" },
        ink: { DEFAULT: "var(--ink)", soft: "var(--soft)", mute: "var(--mute)" },
        oxblood: {
          DEFAULT: "var(--accent)",
          press: "var(--accent-press)",
          soft: "var(--accent-soft)",
          on: "var(--on-accent)",
        },
        state: {
          low: "var(--low)", "low-bg": "var(--low-bg)",
          med: "var(--med)", "med-bg": "var(--med-bg)",
          high: "var(--high)", "high-bg": "var(--high-bg)",
          major: "var(--major)", "major-bg": "var(--major-bg)",
        },
      },
      borderColor: { DEFAULT: "var(--line)", soft: "var(--line-soft)" },
      borderRadius: { tile: "var(--radius)", card: "var(--radius-lg)", pill: "999px" },
      boxShadow: { 1: "var(--shadow)", 2: "var(--shadow-md)", focus: "var(--focus)" },
      maxWidth: { page: "1100px" },
      transitionTimingFunction: {
        spring: "cubic-bezier(.34,1.26,.5,1)",
        emphasized: "cubic-bezier(.05,.7,.1,1)",
      },
    },
  },
  plugins: [],
};
