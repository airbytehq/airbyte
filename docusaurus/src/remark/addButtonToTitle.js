const { select } = require("unist-util-select");
const { u } = require("unist-builder");

const plugin = () => {
  const transformer = async (ast, vfile) => {
    // Find first header in document
    const heading = select("root > mdxJsxFlowElement[name='header']", ast);
    const headingFallback = select("root > heading[depth='1']", ast);
    const targetHeading = heading || headingFallback;

    if (targetHeading) {
      // Create new <CopyForLLMButton /> element
      const buttonNode = u(
        "mdxJsxFlowElement",
        {
          name: "CopyPageButton",
          attributes: [
            {
              type: "mdxJsxAttribute",
              name: "path",
              value: `${vfile.path}.md`,
            },
          ],
        },
        [],
      );

      if (targetHeading.type === "mdxJsxFlowElement") {
        // For JSX elements like <header>, add the className
        const classNameAttr = targetHeading.attributes.find(
          (attr) => attr.name === "className",
        );

        if (classNameAttr) {
          // If className exists, append our class
          if (typeof classNameAttr.value === "string") {
            classNameAttr.value += " header-with-button";
          }
        } else {
          // If no className, add one
          targetHeading.attributes.push({
            type: "mdxJsxAttribute",
            name: "className",
            value: "header-with-button",
          });
        }

        // We'll insert the button as the last child of the header
        targetHeading.children.push(buttonNode);
      } else if (targetHeading.type === "heading") {
        // For regular markdown headings, create a wrapper with className
        const headingIndex = ast.children.findIndex(
          (ch) => ch === targetHeading,
        );

        if (headingIndex !== -1) {
          const wrapperNode = u(
            "mdxJsxFlowElement",
            {
              name: "div",
              attributes: [
                {
                  type: "mdxJsxAttribute",
                  name: "className",
                  value: "header-with-button",
                },
              ],
            },
            [
              targetHeading, // The original heading
              buttonNode, // The button
            ],
          );

          // Replace the original heading with our wrapper
          ast.children[headingIndex] = wrapperNode;
        }
      }
    }
  };
  return transformer;
};

module.exports = plugin;
