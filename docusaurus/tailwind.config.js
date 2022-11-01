/** @type {import('tailwindcss').Config} */
module.exports = {
  corePlugins: {
    preflight: false,
  },
  content: ["./src/**/*.{js,jsx,ts,tsx}", "../docs/**/*.{jsx,md,mdx}", "../docs/.components/**/*.{jsx,md,mdx}"],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {},
  },
  plugins: [
    // for https://headlessui.com/react/combobox
    require('@headlessui/tailwindcss'),
    // https://tailwindui.com/components/application-ui/forms/comboboxes
    require('@tailwindcss/forms')
  ],
}
