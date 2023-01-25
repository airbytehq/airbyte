module.exports = {
  env: {
    browser: true,
    node: true,
  },
  extends: [
    "plugin:cypress/recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier",
    "plugin:prettier/recommended",
  ],
  plugins: ["@typescript-eslint", "prettier"],
  parser: "@typescript-eslint/parser",
  rules: {
    "cypress/no-unnecessary-waiting": "warn",
    "prettier/prettier": "warn",

    curly: "warn",
    "dot-location": ["warn", "property"],
    "dot-notation": "warn",
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

    "@typescript-eslint/no-var-requires": "off",
    "@typescript-eslint/triple-slash-reference": "off",
  },
};
