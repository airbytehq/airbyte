/**
 * This script discovers agent connector directories and writes a manifest file.
 * It's called during the prebuild phase so that the AgentConnectorRegistry
 * component can import the manifest as a tracked dependency. This ensures
 * the build system (Rspack) naturally detects when connectors are added or
 * removed and recompiles the page.
 */
const fs = require("fs");
const path = require("path");
const { AGENT_CONNECTOR_MANIFEST_PATH } = require("./constants");

const CONNECTORS_DIR = path.resolve(__dirname, "../../../docs/ai-agents/connectors");

function discoverAgentConnectorSlugs() {
  try {
    return fs
      .readdirSync(CONNECTORS_DIR, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name)
      .sort();
  } catch (error) {
    console.warn("Failed to discover agent connector directories:", error.message);
    return [];
  }
}

function main() {
  const slugs = discoverAgentConnectorSlugs();

  const dataDir = path.dirname(AGENT_CONNECTOR_MANIFEST_PATH);
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  fs.writeFileSync(
    AGENT_CONNECTOR_MANIFEST_PATH,
    JSON.stringify(slugs, null, 2) + "\n",
  );
  console.log(`Discovered ${slugs.length} agent connectors`);
}

main();
