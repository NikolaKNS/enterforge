import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#080d1a',
          800: '#0a0f2e',
          700: '#0d1f4e',
          600: '#161b22',
        },
        cyan: {
          DEFAULT: '#00b4d8',
          dark: '#0096b4',
        },
        purple: {
          accent: '#9b59b6',
        },
        forge: {
          orange: '#E85D04',
          navy: '#0D1B2A',
          white: '#FFF8F0',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-delayed': 'float 6s ease-in-out infinite 3s',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        }
      }
    },
  },
  plugins: [],
} satisfies Config
