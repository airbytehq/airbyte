const { select } = require("unist-util-select");
const { u } = require('unist-builder');

const plugin = () => {
  const transformer = async (ast, vfile) => {
    // Run only on files that have `products` set in their frontmatter.
    if (!vfile.data?.frontMatter?.products) {
      return;
    }

    // Find first header in document
    const heading = select("root > heading[depth='1']", ast);
    const headingIndex = ast.children.findIndex(ch => ch === heading);
    if (headingIndex) {
      // Create new <ProductInformation products={frontmatter.products} /> element
      const flavorNode = u('mdxJsxFlowElement', {
        name: "ProductInformation",
        attributes: [
          {
            type: "mdxJsxAttribute",
            name: "products",
            value: vfile.data.frontMatter.products,
          }
        ]
      }, []);

      // Add the ProductInformation JSX node right after the first header node
      ast.children.splice(headingIndex + 1, 0, flavorNode);
    }
  };
  return transformer;
};

module.exports = plugin;
