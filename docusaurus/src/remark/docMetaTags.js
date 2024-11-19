const { default: React } = require("react");
const { getFromPaths, toAttributes } = require("../helpers/objects");
const { isDocsPage, getRegistryEntry } = require("./utils");
const visit = require("unist-util-visit").visit;

const generateMetaTags = (connectorName) => {
  return {
    title: `${connectorName} Connector | Airbyte Documentation`,
    description: `Connect ${connectorName} to our ETL/ELT platform for streamlined data integration, automated syncing, and powerful data insights.`,
  };
};
const plugin = () => {
  const transformer = async (ast, vfile) => {
    const docsPageInfo = isDocsPage(vfile);
    if (!docsPageInfo.isDocsPage) return;

    const registryEntry = await getRegistryEntry(vfile);

    if (!registryEntry) return;

    visit(ast, "heading", (node) => {
      const name = getFromPaths(registryEntry, "name_[oss|cloud]");
      console.log("name", name);
      const { title, description } = generateMetaTags(name);

      const attributes = toAttributes({
        title,
        description,
      });

      node.children = [];
      node.type = "mdxJsxFlowElement";
      node.name = "DocMetaTags";
      node.attributes = attributes;
    });
  };
  return transformer;
};

module.exports = plugin;
