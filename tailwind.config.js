/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html'],
  theme: {
    extend: {
      colors: {
        wabi: { black: '#1a1a1a', red: '#c41e3a', gold: '#c5a55a', text: '#f5f5f5', subtle: '#888888' }
      },
      fontFamily: {
        serif: ['"Noto Serif JP"', 'serif'],
        sans: ['"Noto Sans JP"', 'sans-serif'],
      }
    }
  },
  plugins: [],
}
