// eslint-disable-next-line @typescript-eslint/no-var-requires
const stylelint = require("stylelint");
const { ruleMessages } = stylelint.utils;
const ruleName = "airbyte/no-color-variables-in-rgba";
const messages = ruleMessages(ruleName, {
  variableFoundInRgba: () =>
    `A color variable can't be used within an rgba() function. Explanation: ${LINK_TO_STYLEGUIDE}`,
});
const LINK_TO_STYLEGUIDE =
  "https://github.com/airbytehq/airbyte/blob/master/airbyte-webapp/STYLEGUIDE.md#color-variables-cannot-be-used-inside-of-rgba-functions";

module.exports.ruleName = ruleName;
module.exports.messages = messages;

/**
 * This stylelint rule checks if a color variable is used inside of rgba(), which we do not currently support.
 * There are no options passed to the rule, as long as it is enabled in .stylelintrc it will be enforced.
 */
module.exports = (enabled) => {
  return function lint(postcssRoot, postcssResult) {
    if (!enabled) {
      return () => null;
    }
    postcssRoot.walkDecls((decl) => {
      // Check each value to see if it contains a string like "rgba(colors.$" or "rgba( ... colors.$"
      const hasVariableInRgba = /rgba\([^)]*colors\.\$/.test(decl.value);
      if (hasVariableInRgba) {
        stylelint.utils.report({
          ruleName,
          result: postcssResult,
          message: messages.variableFoundInRgba(),
          node: decl,
          word: "blue",
        });
      }
    });
  };
};
