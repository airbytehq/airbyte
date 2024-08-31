const { isEnterpriseConnectorDocsPage } = require("./utils");
const { toAttributes } = require("../helpers/objects");
const visit = require("unist-util-visit").visit;

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const isDocsPage = isEnterpriseConnectorDocsPage(vfile);
    if (!isDocsPage) return;

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
          dockerImageTag: "custom",
          // iconUrl: registryEntry.iconUrl_oss,
          // github_url: registryEntry.github_url,
          // issue_url: registryEntry.issue_url,
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
