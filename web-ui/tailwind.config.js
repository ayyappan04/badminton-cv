/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'neon-green': '#00ff9d',
                'neon-blue': '#00b8ff',
                'dark-bg': '#0a0a0a'
            }
        },
    },
    plugins: [],
}
