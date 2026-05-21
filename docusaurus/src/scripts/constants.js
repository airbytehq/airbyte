const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data");
const REGISTRY_CACHE_PATH = path.join(DATA_DIR, "connector_registry_slim.json");
const AGENT_CONNECTORS_ENABLED_CACHE_PATH = path.join(
  DATA_DIR,
  "agent_connectors.json",
);
const COMPOSITE_REGISTRY_URL =
  "https://connectors.airbyte.com/files/registries/v0/composite_registry.json";
const AGENT_CONNECTORS_REGISTRY_URL =
  "https://connectors.airbyte.ai/registry.json";

// Connector documentation paths
const CONNECTORS_DOCS_ROOT = "../docs/integrations";
const AGENT_CONNECTORS_DOCS_DIR = path.resolve(
  __dirname,
  "../../../docs/ai-agents/connectors",
);
const SOURCES_DOCS = `${CONNECTORS_DOCS_ROOT}/sources`;
const DESTINATIONS_DOCS = `${CONNECTORS_DOCS_ROOT}/destinations`;
const ENTERPRISE_CONNECTORS_DOCS = `${CONNECTORS_DOCS_ROOT}/enterprise-connectors`;

module.exports = {
  DATA_DIR,
  REGISTRY_CACHE_PATH,
  AGENT_CONNECTORS_ENABLED_CACHE_PATH,
  COMPOSITE_REGISTRY_URL,
  AGENT_CONNECTORS_REGISTRY_URL,
  CONNECTORS_DOCS_ROOT,
  AGENT_CONNECTORS_DOCS_DIR,
  SOURCES_DOCS,
  DESTINATIONS_DOCS,
  ENTERPRISE_CONNECTORS_DOCS,
};
