const visit = require("unist-util-visit").visit;
const { toAttributes } = require("../helpers/objects");

const ICON_BASE_URL =
  "https://connectors.airbyte.com/files/metadata/airbyte";

const isAgentConnectorPage = (vfile) => {
  return (
    vfile.path.includes("ai-agents/connectors/") &&
    !vfile.path.toLowerCase().endsWith("connectors/readme.md")
  );
};

const getConnectorSlug = (vfile) => {
  const parts = vfile.path.split("/");
  const connectorsIdx = parts.indexOf("connectors");
  if (connectorsIdx === -1 || connectorsIdx + 1 >= parts.length) return null;
  return parts[connectorsIdx + 1];
};

function formatConnectorName(slug) {
  return slug
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

const plugin = () => {
  const transformer = async (ast, vfile) => {
    if (!isAgentConnectorPage(vfile)) return;

    const slug = getConnectorSlug(vfile);
    if (!slug) return;

    const iconUrl = `${ICON_BASE_URL}/source-${slug}/latest/icon.svg`;
    const connectorName = formatConnectorName(slug);

    let headingTransformed = false;

    visit(ast, "heading", (node) => {
      if (headingTransformed) return;
      if (node.depth !== 1 || node.children.length !== 1) return;

      const originalTitle = node.children[0].value;

      // Transform heading into AgentConnectorTitle
      node.children = [];
      node.type = "mdxJsxFlowElement";
      node.name = "AgentConnectorTitle";
      node.attributes = toAttributes({ iconUrl, originalTitle });

      headingTransformed = true;
    });

    if (!headingTransformed) return;

    // Insert banner at the root level, after the heading node.
    // The heading may be wrapped by Docusaurus (e.g. in a <header> element),
    // so we find it by looking for the transformed AgentConnectorTitle or
    // any wrapper that contains it.
    const headingIdx = ast.children.findIndex(
      (ch) =>
        (ch.type === "mdxJsxFlowElement" && ch.name === "AgentConnectorTitle") ||
        (ch.type === "mdxJsxFlowElement" && ch.name === "header") ||
        (ch.type === "heading" && ch.depth === 1),
    );

    if (headingIdx !== -1) {
      const bannerNode = {
        type: "mdxJsxFlowElement",
        name: "ConnectorTypeBanner",
        attributes: toAttributes({
          connectorType: "agent",
          counterpartUrl: `/integrations/sources/${slug}`,
          connectorName,
        }),
        children: [],
      };
      ast.children.splice(headingIdx + 1, 0, bannerNode);
    }
  };
  return transformer;
};

module.exports = plugin;
