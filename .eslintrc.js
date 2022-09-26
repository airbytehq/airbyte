module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  ignorePatterns: [
    // Don't lint already-built outputs.
    "dist",
    // Don't lint the NPM package directory.
    "node_modules",
    // Uncomment to skip linting of external sources.
    /* "flow_generated/external" */
  ],
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ['./tsconfig.json'],
  },
  plugins: ['@typescript-eslint'],
  extends: [
    // Core eslint recommendations.
    'eslint:recommended',
    // Disable eslint:recommend rules covered by the typescript linter plugin.
    'plugin:@typescript-eslint/eslint-recommended',
    // Enable recommend typescript rules.
    'plugin:@typescript-eslint/recommended',
    // Enable recommend typescript rules which require type information from `tsc`.
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    // Disable rules from @typescript-eslint/eslint-plugin that conflict with prettier
    'prettier/@typescript-eslint',
    // Enable eslint-plugin-prettier and eslint-config-prettier.
    // This will display prettier errors as ESLint errors.
    // This must be last configuration in the extends array.
    'plugin:prettier/recommended'
  ],
  // Opt-in to several additional rules.
  rules:  {
    // Disable camel-case linting, as identifier names are often drawn from JSON-Schemas
    // which are outside of the author's control.
    "@typescript-eslint/camelcase": "off",
    // Allow variables prefixed with underscore to be unused.
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_.*" }],
    // Flow lambdas always return promises, but not all implementations need to be async.
    "@typescript-eslint/require-await": "off",
    // Require that created promises are used (await'd), and not silently dropped.
    "@typescript-eslint/no-floating-promises": "error",
    // Disallow uses of foo?.bar! (it's not possible to know that bar exists, since foo may not).
    "@typescript-eslint/no-non-null-asserted-optional-chain": "error",
    // Require functions returning Promise to be async. This avoids needing to handle a non-async
    // function which can technically throw an Error *OR* return a rejected Promise. With this
    // lint, a function can throw (if non-async) or reject (if async) but never both.
    "@typescript-eslint/promise-function-async": "error",
    // When adding two operands, each must be of type string or number, and cannot mix.
    "@typescript-eslint/restrict-plus-operands": ["error", { "checkCompoundAssignments": true }],
    // Switches over enum types should check all cases (or use explicit "default").
    "@typescript-eslint/switch-exhaustiveness-check": "error",
    // Warn on superfluous checks of boolean types against boolean literals (if (foo: bool === true) {}).
    "@typescript-eslint/no-unnecessary-boolean-literal-compare": "warn",
    // Warn on conditionals which are always truthy or falsy.
    "@typescript-eslint/no-unnecessary-condition": "warn",
    // Warn on "for (let i = 0; i != arr.length; i++)" syntax instead of for-of "for(const i in arr)".
    "@typescript-eslint/prefer-for-of": "warn",
  },
};
