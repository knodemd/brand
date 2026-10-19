// Knode, Tailwind preset: presets: [require("./tailwind-preset")]
module.exports = {
  theme: {
    extend: {
      colors: { ink: "#0B0B14", paper: "#F3F2EE", indigo: { DEFAULT: "#818CF8" }, "terminal-grey": "#6E6D8C" },
      fontFamily: {
        block: ["Knode Block", "monospace"],
        line: ["Knode Line", "monospace"],
        sans: ["Geist", "system-ui", "sans-serif"],
        mono: ["Geist Mono", "ui-monospace", "monospace"],
      },
    },
  },
};
