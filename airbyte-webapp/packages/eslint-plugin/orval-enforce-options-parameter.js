module.exports = {
  name: "orval-enforce-options-parameter",
  meta: {
    type: "suggestion",
    fixable: "code",
  },
  create: (context) => ({
    ArrowFunctionExpression: (node) => {
      const lastParameter = node.params[node.params.length - 1];
      if (
        lastParameter.name === "options" &&
        lastParameter.optional === true &&
        lastParameter.typeAnnotation?.typeAnnotation?.typeName?.name === "SecondParameter"
      ) {
        context.report({
          node,
          message: "Parameter passed forward to apiOverwrite should not be optional.",
          fix(fixer) {
            // Remove the questionmark behind the parameter name
            return fixer.removeRange([
              lastParameter.range[0] + lastParameter.name.length,
              lastParameter.range[0] + lastParameter.name.length + 1,
            ]);
          },
        });
      }
    },
  }),
};
