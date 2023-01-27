// eslint-disable-next-line @typescript-eslint/no-var-requires
const stylelint = require("stylelint");
const { ruleMessages } = stylelint.utils;
const ruleName = "airbyte/no-use-renaming";
const messages = ruleMessages(ruleName, {
  rejected: () => `You should not assign @use imports a different name.`,
});

module.exports.ruleName = ruleName;
module.exports.messages = messages;

/**
 * This stylelint rule checks a `@use` statement got a new name assigned e.g. `@use "scss/variables" as var`
 * and fails if so.
 */
/** @type {import('stylelint').Rule<boolean>} */
module.exports = (enabled) => {
  return function lint(postcssRoot, postcssResult) {
    if (!enabled) {
      return;
    }
    postcssRoot.walkAtRules((rule) => {
      if (rule.name === "use" && rule.params.includes(" as ")) {
        stylelint.utils.report({
          ruleName,
          node: rule,
          message: messages.rejected(),
          result: postcssResult,
          word: `as `,
        });
      }
    });
  };
};
