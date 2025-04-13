// frontend/tailwind.config.js

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
      './src/components/**/*.{js,ts,jsx,tsx,mdx}',
      './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        // Add your custom colors here
        colors: {
          'theme-background': '#fdfdfd', // Background
          'theme-primary': '#111111',    // Primary
          'theme-accent': '#ff3f3f',     // Accent (Red-Pink)
          'theme-secondary': '#3affd6',  // Secondary (Mint Blue)
          'theme-tertiary': '#ffd700',  // Tertiary (Bold Yellow) - Replaced theme-highlight
        },
        // You can also extend other theme properties like fonts if needed
        // fontFamily: {
        //   sans: ['Inter', 'sans-serif'], // Example
        // },
      },
    },
    plugins: [],
  }
