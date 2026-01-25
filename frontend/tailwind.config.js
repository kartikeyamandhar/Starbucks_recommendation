/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Starbucks official colors
        'starbucks-green': '#00704A',
        'starbucks-dark': '#1E3932',
        'starbucks-cream': '#F2F0EB',
        'starbucks-warm': '#D4AF37',
        'neutral-50': '#FAFAF9',
        'neutral-100': '#F5F5F4',
        'neutral-200': '#E7E5E4',
        'neutral-300': '#D6D3D1',
        'neutral-700': '#44403C',
        'neutral-800': '#292524',
        'neutral-900': '#1C1917',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        // Limited font scale: 4 sizes only
        'h1': ['32px', { lineHeight: '40px', fontWeight: '600' }],
        'h2': ['24px', { lineHeight: '32px', fontWeight: '600' }],
        'body': ['16px', { lineHeight: '24px', fontWeight: '400' }],
        'caption': ['14px', { lineHeight: '20px', fontWeight: '400' }],
      },
      spacing: {
        // 8px grid system - no exceptions
        '1': '8px',
        '2': '16px',
        '3': '24px',
        '4': '32px',
        '5': '40px',
        '6': '48px',
        '8': '64px',
        '10': '80px',
      },
      borderRadius: {
        'default': '8px',
        'lg': '12px',
      },
      boxShadow: {
        'soft': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'card': '0 1px 3px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [],
}