/** @type {import('tailwindcss').Config} */
module.exports = {
  // FIX: content paths updated to match the actual project structure.
  // The original pointed to "./src/**" which does not exist in this project —
  // all JS/JSX/CSS files live in the root, not inside a src/ folder.
  content: [
    "./*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("tailwindcss-animate")],
};

