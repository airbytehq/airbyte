const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data");
const REGISTRY_CACHE_PATH = path.join(DATA_DIR, "connector_registry_slim.json");
const REGISTRY_URL =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

// Connector documentation paths
const CONNECTORS_DOCS_ROOT = "../docs/integrations";
const SOURCES_DOCS = `${CONNECTORS_DOCS_ROOT}/sources`;
const DESTINATIONS_DOCS = `${CONNECTORS_DOCS_ROOT}/destinations`;
const ENTERPRISE_CONNECTORS_DOCS = `${CONNECTORS_DOCS_ROOT}/enterprise-connectors`;

module.exports = {
  DATA_DIR,
  REGISTRY_CACHE_PATH,
  REGISTRY_URL,
  CONNECTORS_DOCS_ROOT,
  SOURCES_DOCS,
  DESTINATIONS_DOCS,
  ENTERPRISE_CONNECTORS_DOCS,
};
