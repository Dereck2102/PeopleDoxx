import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        orange: {
          500: '#f97316',
          600: '#ea6c0a',
        },
      },
    },
  },
  plugins: [],
};

export default config;
