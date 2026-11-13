/**
 * Docusaurus plugin that exposes the data replication connectors that have an
 * agent connector equivalent, so connector pages and connector lists can mark them.
 *
 * `ConnectorRegistry` reads this with `usePluginData("agent-connectors-plugin")`,
 * and the `docsHeaderDecoration` remark plugin calls `isAgentConnector` directly.
 */
const agentConnectors = require("../data/agent_connectors.json");

function isAgentConnector(dockerRepository) {
  const match = /^airbyte\/(source|destination)-(.+)$/.exec(
    dockerRepository ?? "",
  );
  if (!match) return false;
  const [, connectorType, slug] = match;
  const slugs =
    connectorType === "destination"
      ? agentConnectors.destinations
      : agentConnectors.sources;
  return slugs.includes(slug);
}

function agentConnectorsPlugin(_context, _options) {
  return {
    name: "agent-connectors-plugin",
    async contentLoaded({ actions }) {
      actions.setGlobalData(agentConnectors);
    },
  };
}

module.exports = agentConnectorsPlugin;
module.exports.isAgentConnector = isAgentConnector;
