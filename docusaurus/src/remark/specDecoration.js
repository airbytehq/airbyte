const visit = require("unist-util-visit").visit;
const catalog = require("../connector_registry");

const plugin = () => {
  const transformer = async (ast, vfile) => {

    const registry = await catalog;

    visit(ast, "mdxJsxFlowElement", (node) => {
      if (node.name !== "SpecSchema" && node.name !== "AirbyteLibExample") return;

      const connectorName = node.attributes.find((attr) => attr.name === "connector").value;
      const connectorSpec = registry.find( (c) => c.dockerRepository_oss === `airbyte/${connectorName}`).spec_oss.connectionSpecification;
      node.attributes.push({
        type: "mdxJsxAttribute",
        name: "specJSON",
        value: JSON.stringify(connectorSpec)
      });
    });
  };
  return transformer;
};

module.exports = plugin;
