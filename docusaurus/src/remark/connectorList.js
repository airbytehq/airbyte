const visit = require("unist-util-visit").visit;
const catalog = require("../connector_registry");

const plugin = () => {
  const transformer = async (ast, vfile) => {

    const registry = await catalog;

    visit(ast, "mdxJsxFlowElement", (node) => {
      if (node.name !== "AirbyteLibConnectors") return;

        const connectors = registry.filter( (c) => (c.tags_oss || []).includes("language:lowcode"));

      node.attributes.push({
        type: "mdxJsxAttribute",
        name: "connectorsJSON",
        value: JSON.stringify(connectors)
      });
    });
  };
  return transformer;
};

module.exports = plugin;