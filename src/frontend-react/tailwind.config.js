/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand colors (from Streamlit app)
        primary: {
          50: '#f0f3ff',
          100: '#e0e8ff',
          200: '#c7d4ff',
          300: '#a4b5ff',
          400: '#8494ff',
          500: '#667eea', // Main primary
          600: '#5d6fd7',
          700: '#4f5fb8',
          800: '#424f94',
          900: '#3a4576',
        },
        secondary: {
          50: '#f7f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#764ba2', // Main secondary
          600: '#6d4190',
          700: '#5b357e',
          800: '#4c2d69',
          900: '#3f2556',
        },
        // Success/opportunity colors
        opportunity: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#11998e', // Quick wins
          600: '#0f8a7f',
          700: '#0e7169',
          800: '#0d5d56',
          900: '#0c4a47',
        },
        // Warning/strategic colors
        strategic: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#ffa726', // Strategic investments
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
        // Error/high-risk colors
        risk: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ff6b6b', // High risk
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 4px 15px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 8px 25px rgba(0, 0, 0, 0.15)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
} 