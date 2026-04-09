const { select } = require("unist-util-select");
const { u } = require("unist-builder");

const plugin = () => {
  const transformer = async (ast, vfile) => {
    // Run only on files that have `plans` set in their frontmatter.
    if (!vfile.data?.frontMatter?.plans) {
      return;
    }

    // Find first header in document
    const heading = select("root > mdxJsxFlowElement[name='header']", ast);
    const headingFallback = select("root > heading[depth='1']", ast);
    const targetHeading = heading || headingFallback;

    const headingIndex = ast.children.findIndex((ch) => ch === targetHeading);
    if (headingIndex) {
      // Create new <PlanInformation plans={frontmatter.plans} /> element
      const planNode = u(
        "mdxJsxFlowElement",
        {
          name: "PlanInformation",
          attributes: [
            {
              type: "mdxJsxAttribute",
              name: "plans",
              value: vfile.data.frontMatter.plans,
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
