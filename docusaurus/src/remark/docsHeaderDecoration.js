const { getFromPaths, toAttributes } = require("../helpers/objects");
const { isDocsPage, getRegistryEntry } = require("./utils");
const {
  getLatestPythonCDKVersion,
  parseCDKVersion,
} = require("../connector_registry");
const visit = require("unist-util-visit").visit;

/**
 * Convert a boolean to a string
 *
 * Why? Because MDX doesn't support passing boolean values properly
 */
const boolToBoolString = (bool) => (bool ? "TRUE" : "FALSE");

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const docsPageInfo = isDocsPage(vfile);
    if (!docsPageInfo.isDocsPage) return;

    const registryEntry = await getRegistryEntry(vfile);
    const latestPythonCdkVersion = await getLatestPythonCDKVersion();

    if (!registryEntry) return;

    let firstHeading = true;

    visit(ast, "heading", (node) => {
      if (firstHeading && node.depth === 1 && node.children.length === 1) {
        const originalTitle = node.children[0].value;
        const originalId = node.data.hProperties.id;

        const rawCDKVersion = getFromPaths(
          registryEntry,
          "packageInfo_[oss|cloud].cdk_version"
        );
        const syncSuccessRate = getFromPaths(
          registryEntry,
          "generated_[oss|cloud].metrics.[all|cloud|oss].sync_success_rate"
        );
        const usageRate = getFromPaths(
          registryEntry,
          "generated_[oss|cloud].metrics.[all|cloud|oss].usage"
        );
        const lastUpdated = getFromPaths(
          registryEntry,
          "generated_[oss|cloud].source_file_info.metadata_last_modified"
        );

        const { version, isLatest, url } = parseCDKVersion(
          rawCDKVersion,
          latestPythonCdkVersion
        );

        const attrDict = {
          isOss: registryEntry.is_oss,
          isCloud: registryEntry.is_cloud,
          supportLevel: registryEntry.supportLevel_oss,
          dockerImageTag: registryEntry.dockerImageTag_oss,
          iconUrl: registryEntry.iconUrl_oss,
          github_url: registryEntry.github_url,
          issue_url: registryEntry.issue_url,
          originalTitle,
          originalId,
          cdkVersion: version,
          isLatestCDKString: boolToBoolString(isLatest),
          cdkVersionUrl: url,
          syncSuccessRate,
          usageRate,
          lastUpdated,
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
