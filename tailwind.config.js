/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./podcasts/templates/**/*.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans']
      },
      colors: {
        'text': '#eaecf0',
        'background': '#070709',
        'primary': '#666d8a',
        'secondary': '#46394c',
        'accent': '#755774',
       },
    },
    container: {
      center: true,
      padding: '1.5rem',
      screens: {
        'sm': '480px',
        'md': '680px',
        'lg': '1080px'
      }
    },
  },
  plugins: [],
}

