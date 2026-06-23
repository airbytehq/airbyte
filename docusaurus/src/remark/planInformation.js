const { select } = require("unist-util-select");
const { u } = require("unist-builder");

const plugin = () => {
  const transformer = async (ast, vfile) => {
    // Run only on files that have `plan` set in their frontmatter.
    if (!vfile.data?.frontMatter?.plan) {
      return;
    }

    // Find first header in document
    const heading = select("root > mdxJsxFlowElement[name='header']", ast);
    const headingFallback = select("root > heading[depth='1']", ast);
    const targetHeading = heading || headingFallback;

    const headingIndex = ast.children.findIndex((ch) => ch === targetHeading);
    if (headingIndex !== -1) {
      // Create new <PlanInformation plans={frontmatter.plan} /> element
      const planNode = u(
        "mdxJsxFlowElement",
        {
          name: "PlanInformation",
          attributes: [
            {
              type: "mdxJsxAttribute",
              name: "plans",
              value: vfile.data.frontMatter.plan,
            },
          ],
        },
        [],
      );

      // Add the PlanInformation JSX node right after the first header node
      ast.children.splice(headingIndex + 1, 0, planNode);
    }
  };
  return transformer;
};

module.exports = plugin;
