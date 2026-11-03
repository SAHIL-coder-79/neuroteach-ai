/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'bg-base': 'var(--bg-base)',
        'bg-surface': 'var(--bg-surface)',
        'bg-raised': 'var(--bg-raised)',
        'border-subtle': 'var(--border-subtle)',
        'border-lavender': 'var(--border-lavender)',
        'accent': {
          50: '#F7F5FF',
          100: '#EEE9FF',
          200: '#DDD5FA',
          300: '#B9A6F7',
          400: '#947BF0',
          500: '#7555D9',
          600: '#6242C5',
          700: '#5033A3',
          lavender: '#EEE9FF',
          cyan: '#0E94A8',
          softcyan: '#E6F8FA',
        },
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-muted': 'var(--text-muted)',
        'success': '#168058',
        'warning': '#C67A18',
        'danger': '#C93B52',
        'info': '#0E94A8',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        'card': '14px',
        'glass': '16px',
      },
    },
  },
  plugins: [],
}
