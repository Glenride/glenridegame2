/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // The 'tg' object maps to the variables we set in the hook
        tg: {
          bg: 'var(--tg-bg)',
          text: 'var(--tg-text)',
          hint: 'var(--tg-hint)',
          link: 'var(--tg-link)',
          button: 'var(--tg-button)',
          'button-text': 'var(--tg-button-text)',
          'secondary-bg': 'var(--tg-secondary-bg)',
        },
        // ADD YOUR BRAND COLORS HERE
        brand: {
          primary: '#FF4500', // Example: distinct orange brand
          accent: '#32CD32',
        }
      },
      fontFamily: {
        // Use a unique font to stand out from standard San Francisco/Roboto
        display: ['"Space Grotesk"', 'sans-serif'], 
      }
    },
  },
  plugins: [],
}
