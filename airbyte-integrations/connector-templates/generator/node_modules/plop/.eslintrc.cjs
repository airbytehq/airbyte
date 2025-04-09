module.exports = {
  env: {
    commonjs: true,
    es2021: true,
    node: true,
  },
  parserOptions: {
    sourceType: "module",
    "allowImportExportEverywhere": true
  },
  extends: ["plugin:prettier/recommended"],
  rules: {
    // https://github.com/plopjs/plop/issues/288
    "linebreak-style": ["error", "unix"],
  },
};
