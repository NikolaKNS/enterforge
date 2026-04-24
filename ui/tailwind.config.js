/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: '#7cb87c',
        'accent-bg': 'rgba(124, 184, 124, 0.1)',
        sidebar: '#1a1a1a',
        'sidebar-text': '#ffffff',
        'sidebar-muted': '#9ca3af',
        'nav-active': '#7cb87c',
      },
    },
  },
  plugins: [],
}
