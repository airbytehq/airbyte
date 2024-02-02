const visit = require("unist-util-visit").visit;
const { catalog, isPypiConnector } = require("../connector_registry");
const { isDocsPage, getRegistryEntry } = require("./utils");

const plugin = () => {
  const transformer = async (ast, vfile) => {
    await injectDefaultAirbyteLibSection(vfile, ast);
    await injectSpecSchema(ast);
  };
  return transformer;
};

async function injectSpecSchema(ast) {
  const registry = await catalog;
  visit(ast, "mdxJsxFlowElement", (node) => {
    if (node.name !== "SpecSchema" && node.name !== "AirbyteLibExample") return;

    const connectorName = node.attributes.find((attr) => attr.name === "connector").value;
    const connectorSpec = registry.find((c) => c.dockerRepository_oss === `airbyte/${connectorName}`).spec_oss.connectionSpecification;
    node.attributes.push({
      type: "mdxJsxAttribute",
      name: "specJSON",
      value: JSON.stringify(connectorSpec)
    });
  });
}

async function injectDefaultAirbyteLibSection(vfile, ast) {
  const registryEntry = await getRegistryEntry(vfile);
  if (!isDocsPage(vfile) || !registryEntry || !isPypiConnector(registryEntry) || vfile.value.includes("## Usage with airbyte-lib")) {
    return;
  }
  const connectorName = registryEntry.dockerRepository_oss.split("/").pop();

  let added = false;
  visit(ast, "heading", (node, index, parent) => {
    if (!added && isChangelogHeading(node)) {
      added = true;
      parent.children.splice(index, 0, {
        type: "heading",
        depth: 2,
        children: [{ type: "text", value: "Reference" }]
      }, {
        type: "mdxJsxFlowElement",
        name: "SpecSchema",
        attributes: [
          {
            type: "mdxJsxAttribute",
            name: "connector",
            value: connectorName
          },
        ]
      });
    }
  });
  if (!added) {
    throw new Error(`Could not find a changelog heading in ${vfile.path} to add the default airbyte-lib section. This connector won't have a reference section. Make sure there is either a ## Changelog section or add a manual reference section.`);
  }
}

function isChangelogHeading(node) {
  return node.depth === 2 && node.children.length === 1 && node.children[0].value.toLowerCase() === "changelog";
}


module.exports = plugin;
