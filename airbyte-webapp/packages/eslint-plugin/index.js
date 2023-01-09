module.exports = {
  rules: {
    "no-hardcoded-connector-ids": require("./no-hardcoded-connector-ids"),
  },
  configs: {
    recommended: {
      rules: {
        "@airbyte/no-hardcoded-connector-ids": "error",
      },
    },
  },
};
