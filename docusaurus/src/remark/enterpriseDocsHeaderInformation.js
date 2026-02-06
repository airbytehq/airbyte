const { isEnterpriseConnectorDocsPage } = require("./utils");
const { toAttributes } = require("../helpers/objects");
const visit = require("unist-util-visit").visit;
const { fetchRegistry } = require("../scripts/fetch-registry");

const FALLBACK_VERSION = "No version information available";
const FALLBACK_DEFINITION_ID = "No definition ID available.";

const getEnterpriseConnectorRegistryInfo = async (dockerRepository) => {
  if (!dockerRepository) {
    return {
      version: FALLBACK_VERSION,
      definitionId: FALLBACK_DEFINITION_ID,
    };
  }
  try {
    const registry = await fetchRegistry();

    const registryEntry = registry.find(
      (r) =>
        r.dockerRepository_oss === dockerRepository ||
        r.dockerRepository_cloud === dockerRepository,
    );
    if (!registryEntry) {
      return {
        version: FALLBACK_VERSION,
        definitionId: FALLBACK_DEFINITION_ID,
      };
    }
    return {
      version:
        registryEntry.dockerImageTag_oss || registryEntry.dockerImageTag_cloud,
      definitionId: registryEntry.definitionId || FALLBACK_DEFINITION_ID,
    };
  } catch (error) {
    console.warn(`[Enterprise Connector Debug] Error fetching version:`, error);
  }

  return {
    version: FALLBACK_VERSION,
    definitionId: FALLBACK_DEFINITION_ID,
  };
};

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const isDocsPage = isEnterpriseConnectorDocsPage(vfile);
    if (!isDocsPage) return;

    const { version, definitionId } = await getEnterpriseConnectorRegistryInfo(
      vfile.data.frontMatter.dockerRepository,
    );

    let firstHeading = true;

    visit(ast, "heading", (node) => {
      if (firstHeading && node.depth === 1 && node.children.length === 1) {
        const originalTitle = node.children[0].value;

        const attrDict = {
          isOss: false,
          isCloud: false,
          isPypiPublished: false,
          isEnterprise: true,
          supportLevel: "enterprise",
          dockerImageTag: version,
          github_url: undefined,
          originalTitle,
          "enterprise-connector":
            vfile.data.frontMatter["enterprise-connector"] || true,
          definitionId,
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
