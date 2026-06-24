/**
 * Docusaurus plugin that discovers public agent connector directories at build time
 * and exposes their slugs via global plugin data.
 */
const {
  discoverAgentConnectorSlugs,
  filterEnabledAgentConnectorSlugs,
} = require("../scripts/agent-connector-availability");

function agentConnectorsPlugin(_context, _options) {
  return {
    name: "agent-connectors-plugin",
    async loadContent() {
      return filterEnabledAgentConnectorSlugs(discoverAgentConnectorSlugs());
    },
    async contentLoaded({ content, actions }) {
      const { setGlobalData } = actions;
      setGlobalData({ slugs: content });
    },
  };
}

module.exports = agentConnectorsPlugin;
