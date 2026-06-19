/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        navy:    { DEFAULT: '#0B2545', dark: '#061830', light: '#16386B' },
        charcoal:{ DEFAULT: '#1A1D29', light: '#252938' },
        lime:    { DEFAULT: '#C6FF3D', dark: '#9FD426' },
        canvas:  '#F6F7FB',
      },
      fontFamily: { sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'] },
      boxShadow: {
        card: '0 2px 8px rgba(11, 37, 69, 0.06), 0 1px 2px rgba(11, 37, 69, 0.04)',
      },
    },
  },
  plugins: [],
}