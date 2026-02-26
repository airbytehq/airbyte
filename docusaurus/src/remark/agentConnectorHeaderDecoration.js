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

const plugin = () => {
  const transformer = async (ast, vfile) => {
    if (!isAgentConnectorPage(vfile)) return;

    const slug = getConnectorSlug(vfile);
    if (!slug) return;

    const iconUrl = `${ICON_BASE_URL}/source-${slug}/latest/icon.svg`;

    let firstHeading = true;

    visit(ast, "heading", (node) => {
      if (firstHeading && node.depth === 1 && node.children.length === 1) {
        const originalTitle = node.children[0].value;

        const attrDict = {
          iconUrl,
          originalTitle,
        };

        firstHeading = false;
        node.children = [];
        node.type = "mdxJsxFlowElement";
        node.name = "AgentConnectorTitle";
        node.attributes = toAttributes(attrDict);
      }
    });
  };
  return transformer;
};

module.exports = plugin;
