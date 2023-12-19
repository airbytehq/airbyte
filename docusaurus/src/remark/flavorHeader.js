const { select } = require("unist-util-select");
const { u } = require('unist-builder');

const plugin = () => {
  const transformer = async (ast, vfile) => {
    // Run only on files that have `flavors` set in their frontmatter.
    if (!vfile.data?.frontMatter?.flavors) {
      return;
    }

    // Find first header in document
    const heading = select("root > heading[depth='1']", ast);
    const headingIndex = ast.children.findIndex(ch => ch === heading);
    if (headingIndex) {
      // Create new <FlavorInformation flavors={frontmatter.flavors} /> element
      const flavorNode = u('mdxJsxFlowElement', {
        name: "FlavorInformation",
        attributes: [
          {
            type: "mdxJsxAttribute",
            name: "flavors",
            value: vfile.data.frontMatter.flavors,
          }
        ]
      }, []);

      // Add the FlavorInformation JSX node right after the first header node
      ast.children.splice(headingIndex + 1, 0, flavorNode);
    }
  };
  return transformer;
};

module.exports = plugin;
