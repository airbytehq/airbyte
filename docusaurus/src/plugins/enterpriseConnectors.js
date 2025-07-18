const fs = require("fs");

const connectorsDocsRoot = "../docs/integrations";
const enterpriseConnectorDocs = `${connectorsDocsRoot}/enterprise-connectors`;

export function getFilenamesInDir(dir, excludes) {
  return fs
    .readdirSync(dir)
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
    .filter((fileName) => excludes.indexOf(fileName.toLowerCase()) === -1);
}

function enterpriseConnectorsPlugin(context, options) {
  return {
    name: "enterprise-connectors-plugin",
    async loadContent() {
      try {
        const enterpriseSources = getFilenamesInDir(enterpriseConnectorDocs, [
          "readme",
        ]);
        return enterpriseSources;
      } catch (e) {
        console.warn(
          "Could not read enterprise connectors directory:",
          e.message,
        );
      }
    },
    async contentLoaded({ content, actions }) {
      const { createData, setGlobalData } = actions;

      const dataPath = await createData(
        "enterprise-connectors.json",
        JSON.stringify(content, null, 2),
      );

      setGlobalData({
        enterpriseConnectors: content,
      });
    },
  };
}

module.exports = enterpriseConnectorsPlugin;
