module.exports = {
  extends: [
    "react-app",
    "plugin:@typescript-eslint/recommended",
    "plugin:jest/recommended",
    "prettier",
    "plugin:prettier/recommended",
    "plugin:css-modules/recommended",
    "plugin:jsx-a11y/recommended",
    "plugin:@airbyte/recommended",
  ],
  plugins: ["react", "@typescript-eslint", "prettier", "unused-imports", "css-modules", "jsx-a11y", "@airbyte"],
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    "jsx-a11y/label-has-associated-control": "error",
    curly: "warn",
    "css-modules/no-undef-class": "off",
    "css-modules/no-unused-class": ["error", { camelCase: true }],
    "dot-location": "warn",
    "dot-notation": "warn",
    eqeqeq: "error",
    "prettier/prettier": "warn",
    "unused-imports/no-unused-imports": "warn",
    "no-else-return": "warn",
    "no-lonely-if": "warn",
    "no-inner-declarations": "off",
    "no-unused-vars": "off",
    "no-useless-computed-key": "warn",
    "no-useless-return": "warn",
    "no-var": "warn",
    "object-shorthand": ["warn", "always"],
    "prefer-arrow-callback": "warn",
    "prefer-const": "warn",
    "prefer-destructuring": ["warn", { AssignmentExpression: { array: true } }],
    "prefer-object-spread": "warn",
    "prefer-template": "warn",
    "spaced-comment": ["warn", "always", { markers: ["/"] }],
    yoda: "warn",
    "import/order": [
      "warn",
      {
        "newlines-between": "always",
        groups: ["type", "builtin", "external", "internal", ["parent", "sibling"], "index"],
        pathGroupsExcludedImportTypes: ["builtin"],
        pathGroups: [
          {
            pattern: "components{/**,}",
            group: "internal",
          },
          {
            pattern: "+(config|core|hooks|locales|packages|pages|services|types|utils|views){/**,}",
            group: "internal",
            position: "after",
          },
        ],
        alphabetize: {
          order: "asc" /* sort in ascending order. Options: ['ignore', 'asc', 'desc'] */,
          caseInsensitive: true /* ignore case. Options: [true, false] */,
        },
      },
    ],
    "@typescript-eslint/array-type": ["warn", { default: "array-simple" }],
    "@typescript-eslint/ban-ts-comment": [
      "warn",
      {
        "ts-expect-error": "allow-with-description",
      },
    ],
    "@typescript-eslint/ban-types": "warn",
    "@typescript-eslint/consistent-indexed-object-style": ["warn", "record"],
    "@typescript-eslint/consistent-type-definitions": ["warn", "interface"],
    "@typescript-eslint/no-unused-vars": "warn",
    "react/function-component-definition": [
      "warn",
      {
        namedComponents: "arrow-function",
        unnamedComponents: "arrow-function",
      },
    ],
    "jest/consistent-test-it": ["warn", { fn: "it", withinDescribe: "it" }],
    "react/no-danger": "error",
    "react/jsx-boolean-value": "warn",
    "react/jsx-curly-brace-presence": "warn",
    "react/jsx-fragments": "warn",
    "react/jsx-no-useless-fragment": ["warn", { allowExpressions: true }],
    "react/self-closing-comp": "warn",
    "react/style-prop-object": ["warn", { allow: ["FormattedNumber"] }],
    "no-restricted-imports": [
      "error",
      {
        paths: [
          {
            name: "lodash",
            message: 'Please use `import [function] from "lodash/[function]";` instead.',
          },
        ],
        patterns: ["!lodash/*"],
      },
    ],
  },
  parser: "@typescript-eslint/parser",
  overrides: [
    {
      files: ["scripts/**/*", "packages/**/*"],
      rules: {
        "@typescript-eslint/no-var-requires": "off",
      },
    },
    {
      // Only applies to files in src. Rules should be in here that are requiring type information
      // and thus require the below parserOptions.
      files: ["src/**/*"],
      parserOptions: {
        tsconfigRootDir: __dirname,
        project: "./tsconfig.json",
      },
      rules: {
        "@typescript-eslint/await-thenable": "warn",
        "@typescript-eslint/no-unnecessary-type-assertion": "warn",
      },
    },
  ],
};
