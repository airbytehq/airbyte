const visit = require("unist-util-visit").visit;
const { fetchRegistry } = require("../scripts/fetch-registry");
const fs = require("fs");
const { ENTERPRISE_CONNECTORS_DOCS } = require("../scripts/constants");

function getEnterpriseConnectorNames() {
  try {
    return fs
      .readdirSync(ENTERPRISE_CONNECTORS_DOCS)
      .filter(
        (fileName) =>
          !(
            fileName.endsWith(".inapp.md") ||
            fileName.endsWith("-migrations.md") ||
            fileName.endsWith(".js") ||
            fileName === "low-code.md"
          ),
      )
      .map((fileName) => fileName.replace(".md", ""))
      .filter((fileName) => fileName.toLowerCase() !== "readme");
  } catch {
    return [];
  }
}

const plugin = () => {
  const transformer = async (ast) => {
    const registry = await fetchRegistry();
    const enterpriseConnectorNames = getEnterpriseConnectorNames();

    visit(ast, "mdxJsxFlowElement", (node) => {
      if (node.name !== "ConnectorRegistry") return;

      const typeAttr = node.attributes.find((attr) => attr.name === "type");
      if (!typeAttr) return;

      const type = typeAttr.value;

      const connectors = registry
        .filter((c) => c.connector_type === type)
        .filter((c) => c.name_oss)
        .filter((c) => c.supportLevel_oss);

      const enterpriseFromRegistry = registry.filter(
        (c) =>
          c.connector_type === type &&
          (c.documentationUrl_oss?.includes(
            "/integrations/enterprise-connectors/",
          ) ||
            c.documentationUrl_cloud?.includes(
              "/integrations/enterprise-connectors/",
            )),
      );

      const enterpriseFromPlugin = enterpriseConnectorNames
        .filter((name) => name.includes(type))
        .map((name) => {
          const _name = name.replace(`${type}-`, "");
          return registry.find(
            (c) =>
              c.name_oss?.includes(_name) ||
              c.name_cloud?.includes(_name) ||
              c.documentationUrl_oss?.includes(_name) ||
              c.documentationUrl_cloud?.includes(_name),
          );
        })
        .filter(Boolean);

      const allEnterprise = [...enterpriseFromRegistry, ...enterpriseFromPlugin];
      const uniqueEnterprise = Array.from(
        new Map(allEnterprise.map((c) => [c.definitionId, c])).values(),
      );

      node.attributes.push({
        type: "mdxJsxAttribute",
        name: "connectorsJSON",
        value: JSON.stringify(connectors),
      });

      node.attributes.push({
        type: "mdxJsxAttribute",
        name: "enterpriseConnectorsJSON",
        value: JSON.stringify(uniqueEnterprise),
      });
    });
  };
  return transformer;
};

module.exports = plugin;
