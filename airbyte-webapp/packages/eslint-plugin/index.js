module.exports = {
  rules: {
    "no-hardcoded-connector-ids": require("./no-hardcoded-connector-ids"),
    "orval-enforce-options-parameter": require("./orval-enforce-options-parameter"),
  },
  configs: {
    recommended: {
      rules: {
        "@airbyte/no-hardcoded-connector-ids": "error",
      },
    },
  },
};
