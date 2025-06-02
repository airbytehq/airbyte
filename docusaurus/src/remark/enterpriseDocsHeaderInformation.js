const { isEnterpriseConnectorDocsPage } = require("./utils");
const { toAttributes } = require("../helpers/objects");
const visit = require("unist-util-visit").visit;
const { catalog } = require("../connector_registry");

const getEnterpriseConnectorVersion = async (dockerRepository) => {
  if (!dockerRepository) {
    return "No version information available";
  }
  try {
    const registry = await catalog;

    const registryEntry = registry.find(
      (r) =>
        r.dockerRepository_oss === dockerRepository ||
        r.dockerRepository_cloud === dockerRepository,
    );
    if (!registryEntry) {
      return "No version information available";
    }
    return (
      registryEntry.dockerImageTag_oss || registryEntry.dockerImageTag_cloud
    );
  } catch (error) {
    console.warn(`[Enterprise Connector Debug] Error fetching version:`, error);
  }

  return "No version information available";
};

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const isDocsPage = isEnterpriseConnectorDocsPage(vfile);
    if (!isDocsPage) return;

    const version = await getEnterpriseConnectorVersion(
      vfile.data.frontMatter.dockerRepository,
    );

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
          supportLevel: "enterprise",
          dockerImageTag: version,
          github_url: undefined,
          originalTitle,
          originalId,
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
