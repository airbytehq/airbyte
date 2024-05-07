const visit = require("unist-util-visit").visit;
const { isDocsPage, getRegistryEntry } = require("./utils");
const { isPypiConnector } = require("../connector_registry");

const toAttributes = (props) =>
  Object.entries(props).map(([key, value]) => ({
    type: "mdxJsxAttribute",
    name: key,
    value: value,
  }));

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const docsPageInfo = isDocsPage(vfile);
    if (!docsPageInfo.isDocsPage) return;

    const registryEntry = await getRegistryEntry(vfile);

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
          isPypiPublished: isPypiConnector(registryEntry),
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

module.exports = plugin;
