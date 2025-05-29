const { isEnterpriseConnectorDocsPage } = require("./utils");
const { toAttributes } = require("../helpers/objects");
const visit = require("unist-util-visit").visit;
const { catalog } = require("../connector_registry");

const getEnterpriseConnectorVersion = async (dockerRepository) => {
  try {
    const registry = await catalog;
    const registryEntry = registry.find(
      (r) => r.dockerRepository_oss === dockerRepository
    );
    
    if (registryEntry && registryEntry.dockerImageTag_oss) {
      return registryEntry.dockerImageTag_oss;
    }
  } catch (error) {
    console.warn(`Error fetching version for ${dockerRepository}:`, error);
  }
  
  return "custom"; // Fallback to "custom" if version not found
};

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const isDocsPage = isEnterpriseConnectorDocsPage(vfile);
    if (!isDocsPage) return;

    const pathParts = vfile.path.split("/");
    let connectorType = "";
    let connectorName = "";
    
    for (let i = 0; i < pathParts.length; i++) {
      if (pathParts[i] === "enterprise-connectors" && i > 0) {
        if (i + 1 < pathParts.length) {
          const fileName = pathParts[i + 1];
          if (fileName.startsWith("source-")) {
            connectorType = "sources";
            connectorName = fileName.replace("source-", "").split(".")[0];
          } else if (fileName.startsWith("destination-")) {
            connectorType = "destinations";
            connectorName = fileName.replace("destination-", "").split(".")[0];
          }
          break;
        }
      }
    }
    
    const dockerRepository = connectorName ? 
      `airbyte/${connectorType.replace(/s$/, "")}-${connectorName}` : "";
    
    const version = dockerRepository ? 
      await getEnterpriseConnectorVersion(dockerRepository) : "custom";

    let firstHeading = true;

    visit(ast, "heading", (node) => {
      if (firstHeading && node.depth === 1 && node.children.length === 1) {
        const originalTitle = node.children[0].value;
        const originalId = node.data.hProperties.id;

        const attrDict = {
          isOss: false,
          isCloud: false,
          isPypiPublished: false,
          isEnterprise: true,
          supportLevel: "certified",
          dockerImageTag: version,
          github_url: dockerRepository ? 
            `https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/${connectorType.replace(/s$/, "")}-${connectorName}` : 
            undefined,
          originalTitle,
          originalId,
          // cdkVersion: version,
          // isLatestCDKString: boolToBoolString(isLatest),
          // cdkVersionUrl: url,
          // syncSuccessRate,
          // usageRate,
          // lastUpdated,
        };

        firstHeading = false;
        node.children = [];
        node.type = "mdxJsxFlowElement";
        node.name = "HeaderDecoration";
        node.attributes = toAttributes(attrDict);
      }
    });
  };
  return transformer;
};

module.exports = plugin;
