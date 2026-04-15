const { select } = require("unist-util-select");
const { u } = require("unist-builder");
const { toAttributes } = require("../helpers/objects");
const { isDocsPage } = require("./utils");

let agentConnectorSlugs = null;

function loadAgentConnectorSlugs() {
  if (agentConnectorSlugs !== null) return agentConnectorSlugs;
  try {
    agentConnectorSlugs = require("../data/agent_connectors.json");
  } catch {
    agentConnectorSlugs = [];
  }
  return agentConnectorSlugs;
}

/**
 * Extract the connector slug from a DR connector page path.
 * e.g. "integrations/sources/hubspot.md" -> "hubspot"
 */
function getSourceSlug(vfile) {
  if (!vfile.path.includes("integrations/sources")) return null;

  const pathParts = vfile.path.split("/");
  const sourcesIdx = pathParts.indexOf("sources");
  if (sourcesIdx === -1 || sourcesIdx + 1 >= pathParts.length) return null;

  return pathParts[sourcesIdx + 1].split(".")[0];
}

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const docsPageInfo = isDocsPage(vfile);
    if (!docsPageInfo.isTrueDocsPage) return;

    const slug = getSourceSlug(vfile);
    if (!slug) return;

    const slugs = loadAgentConnectorSlugs();
    if (!slugs.includes(slug)) return;

    const connectorName = slug
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

    // Find the first heading (which may already be transformed to an mdxJsxFlowElement by docsHeaderDecoration)
    const heading =
      select("root > mdxJsxFlowElement[name='HeaderDecoration']", ast) ||
      select("root > heading[depth='1']", ast);

    if (!heading) return;

    const headingIndex = ast.children.findIndex((ch) => ch === heading);
    if (headingIndex === -1) return;

    const bannerNode = u(
      "mdxJsxFlowElement",
      {
        name: "ConnectorTypeBanner",
        attributes: toAttributes({
          connectorType: "data-replication",
          counterpartUrl: `/ai-agents/connectors/${slug}/`,
          connectorName,
        }),
      },
      [],
    );

    // Insert after the heading (and after any ProductInformation that may have been added)
    // Find the right insertion point: after heading and any immediately following mdxJsxFlowElement nodes
    let insertIdx = headingIndex + 1;
    while (
      insertIdx < ast.children.length &&
      ast.children[insertIdx].type === "mdxJsxFlowElement" &&
      ast.children[insertIdx].name === "ProductInformation"
    ) {
      insertIdx++;
    }

    ast.children.splice(insertIdx, 0, bannerNode);
  };
  return transformer;
};

module.exports = plugin;
