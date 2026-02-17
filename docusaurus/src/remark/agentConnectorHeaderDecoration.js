const visit = require("unist-util-visit").visit;
const { toAttributes } = require("../helpers/objects");
const fs = require("fs");

const ICON_BASE_URL =
  "https://connectors.airbyte.com/files/metadata/airbyte";

const isAgentConnectorPage = (vfile) => {
  return (
    vfile.path.includes("ai-agents/connectors/") &&
    !vfile.path.toLowerCase().endsWith("connectors/readme.md")
  );
};

const isAgentConnectorIndex = (vfile) => {
  return vfile.path.toLowerCase().endsWith("ai-agents/connectors/readme.md");
};

const getConnectorSlug = (vfile) => {
  const parts = vfile.path.split("/");
  const connectorsIdx = parts.indexOf("connectors");
  if (connectorsIdx === -1 || connectorsIdx + 1 >= parts.length) return null;
  return parts[connectorsIdx + 1];
};

const getConnectorsDir = (vfile) => {
  const idx = vfile.path.indexOf("ai-agents/connectors/");
  if (idx === -1) return null;
  return vfile.path.substring(0, idx) + "ai-agents/connectors";
};

const discoverConnectorSlugs = (connectorsDir) => {
  try {
    return fs
      .readdirSync(connectorsDir, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name)
      .sort();
  } catch {
    return [];
  }
};

const plugin = () => {
  const transformer = async (ast, vfile) => {
    if (isAgentConnectorIndex(vfile)) {
      const connectorsDir = getConnectorsDir(vfile);
      if (!connectorsDir) return;

      const slugs = discoverConnectorSlugs(connectorsDir);

      visit(ast, "mdxJsxFlowElement", (node) => {
        if (node.name === "AgentConnectorRegistry") {
          node.attributes = toAttributes({
            connectors: JSON.stringify(slugs),
          });
        }
      });
      return;
    }

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
