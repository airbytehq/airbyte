const visit = require("unist-util-visit").visit;
const catalog = require("../connector_registry");

const toAttributes = (props) =>
  Object.entries(props).map(([key, value]) => ({
    type: "mdxJsxAttribute",
    name: key,
    value: value,
  }));

const plugin = () => {
  const transformer = async (ast, vfile) => {
    if (!isDocsPage(vfile)) return;

    const pathParts = vfile.path.split("/");
    const connectorName = pathParts.pop().split(".")[0];
    const connectorType = pathParts.pop();
    const dockerRepository = `airbyte/${connectorType.replace(
      /s$/,
      ""
    )}-${connectorName}`;

    const registry = await catalog;

    const registryEntry = registry.find(
      (r) => r.dockerRepository_oss === dockerRepository
    );

    if (!registryEntry) return;

    let firstHeading = true;

    visit(ast, "heading", (node) => {
      if (firstHeading && node.depth === 1 && node.children.length === 1) {
        const originalTitle = node.children[0].value;
        const originalId = node.data.hProperties.id;

        firstHeading = false;
        node.children = [];
        node.type = "mdxJsxFlowElement";
        node.name = "HeaderDecoration";
        node.attributes = toAttributes({
          isOss: registryEntry.is_oss,
          isCloud: registryEntry.is_cloud,
          isPypiPublished: Boolean(registryEntry.remoteRegistries?.pypi?.enabled),
          supportLevel: registryEntry.supportLevel_oss,
          dockerImageTag: registryEntry.dockerImageTag_oss,
          iconUrl: registryEntry.iconUrl_oss,
          github_url: registryEntry.github_url,
          issue_url: registryEntry.issue_url,
          originalTitle,
          originalId,
        });
      }
    });
  };
  return transformer;
};

const isDocsPage = (vfile) => {
  if (
    !vfile.path.includes("integrations/sources") &&
    !vfile.path.includes("integrations/destinations")
  ) {
    return false;
  }

  if (vfile.path.includes("-migrations.md")) {
    return false;
  }

  return true;
};

module.exports = plugin;
