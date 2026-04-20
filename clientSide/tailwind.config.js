/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        'chat-float': {
          '0%, 100%': { transform: 'translateY(0) scale(1)' },
          '50%': { transform: 'translateY(-4px) scale(1.02)' },
        },
        'chat-shimmer': {
          '0%': { backgroundPosition: '200% center' },
          '100%': { backgroundPosition: '-200% center' },
        },
        'robot-idle': {
          '0%, 100%': { transform: 'translateY(0) rotate(-1deg)' },
          '50%': { transform: 'translateY(-3px) rotate(1deg)' },
        },
        'robot-think': {
          '0%, 100%': { transform: 'translateY(0) scale(1)' },
          '25%': { transform: 'translateY(-4px) scale(1.03) rotate(-2deg)' },
          '75%': { transform: 'translateY(-2px) scale(1.02) rotate(2deg)' },
        },
        'robot-dot': {
          '0%, 80%, 100%': { transform: 'translateY(0)', opacity: '0.45' },
          '40%': { transform: 'translateY(-3px)', opacity: '1' },
        },
        'lung-breathe': {
          '0%, 100%': { transform: 'scale(1, 1)' },
          '50%': { transform: 'scale(1.04, 1.07)' },
        },
      },
      animation: {
        'chat-float': 'chat-float 4s ease-in-out infinite',
        'chat-shimmer': 'chat-shimmer 8s linear infinite',
        'robot-idle': 'robot-idle 3s ease-in-out infinite',
        'robot-think': 'robot-think 0.55s ease-in-out infinite',
        'robot-dot': 'robot-dot 1s ease-in-out infinite',
        'lung-breathe': 'lung-breathe 2.8s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}

