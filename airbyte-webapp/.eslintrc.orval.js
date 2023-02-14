module.exports = {
  plugins: ["@airbyte", "@typescript-eslint"],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    sourceType: "module",
  },
  rules: {
    "@airbyte/orval-enforce-options-parameter": "warn",
  },
};
