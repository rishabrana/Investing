/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1E40AF',      // Deep Blue
        secondary: '#059669',    // Green (positive)
        danger: '#DC2626',       // Red (negative)
        neutral: '#64748B',      // Slate Gray
        background: '#F8FAFC',   // Light Gray
        'card-bg': '#FFFFFF',    // White
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
