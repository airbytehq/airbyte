/**
 * Docusaurus plugin that discovers agent connector directories at build time
 * and exposes their slugs via global plugin data.
 *
 * The `AgentConnectorRegistry` React component reads this data with
 * `usePluginData("agent-connectors-plugin")` — no JSON file is written to disk
 * and no prebuild script is required. Docusaurus/Rspack invalidates the build
 * when `loadContent` re-runs (e.g. on restart or when watched files change).
 */
const fs = require("fs");
const path = require("path");

const CONNECTORS_DIR = path.resolve(
  __dirname,
  "../../../docs/ai-agents/connectors",
);

function discoverAgentConnectorSlugs() {
  try {
    return fs
      .readdirSync(CONNECTORS_DIR, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name)
      .sort();
  } catch (error) {
    console.warn(
      "Could not read agent connectors directory:",
      error.message,
    );
    return [];
  }
}

function agentConnectorsPlugin(_context, _options) {
  return {
    name: "agent-connectors-plugin",
    async loadContent() {
      return discoverAgentConnectorSlugs();
    },
    async contentLoaded({ content, actions }) {
      const { setGlobalData } = actions;
      setGlobalData({ slugs: content });
    },
  };
}

module.exports = agentConnectorsPlugin;
