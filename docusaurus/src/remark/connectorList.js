const visit = require("unist-util-visit").visit;
const {  isPypiConnector } = require("../scripts/connector_registry");
const  { fetchRegistry } = require("../scripts/fetch-registry");

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const registry = await fetchRegistry();

    visit(ast, "mdxJsxFlowElement", (node) => {
      if (node.name !== "PyAirbyteConnectors") return;

      const connectors = registry.filter(isPypiConnector);

      node.attributes.push({
        type: "mdxJsxAttribute",
        name: "connectorsJSON",
        value: JSON.stringify(connectors),
      });
    });
  };
  return transformer;
};

module.exports = plugin;
