// eslint-disable-next-line @typescript-eslint/no-var-requires
const stylelint = require("stylelint");

const rules = {
  "no-color-variables-in-rgba": require("./no-color-variables-in-rgba"),
};

const rulesPlugins = Object.keys(rules).map((ruleName) =>
  stylelint.createPlugin(`airbyte/${ruleName}`, rules[ruleName])
);

module.exports = rulesPlugins;
