// FIX: This file was missing entirely from the original project.
// Tailwind CSS v3 requires a PostCSS config so that CRA's build pipeline
// processes the @tailwind directives in index.css. Without this file,
// all @tailwind base/components/utilities directives are silently ignored
// and no Tailwind utility classes are generated.
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};

