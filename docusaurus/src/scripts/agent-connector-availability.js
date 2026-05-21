const fs = require("fs");
const https = require("https");
const path = require("path");
const {
  AGENT_CONNECTORS_DOCS_DIR,
  AGENT_CONNECTORS_ENABLED_CACHE_PATH,
  AGENT_CONNECTORS_REGISTRY_URL,
} = require("./constants");

const PLATFORM_ENABLED = "enabled";

function fetchJsonFromUrl(url) {
  return new Promise((resolve, reject) => {
    https
      .get(
        url,
        { headers: { "User-Agent": "airbyte-docs-build" } },
        (response) => {
          if (response.statusCode !== 200) {
            reject(new Error(`Failed to fetch ${url}: ${response.statusCode}`));
            return;
          }

          let data = "";

          response.on("data", (chunk) => {
            data += chunk;
          });

          response.on("end", () => {
            try {
              resolve(JSON.parse(data));
            } catch (error) {
              reject(
                new Error(`Failed to parse data from ${url}: ${error.message}`),
              );
            }
          });
        },
      )
      .on("error", (error) => {
        reject(new Error(`Network error fetching ${url}: ${error.message}`));
      });
  });
}

function slugifyConnectorName(connectorName) {
  return String(connectorName || "")
    .trim()
    .toLowerCase()
    .replace(/_/g, "-")
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function slugFromDocsUrl(docsUrl) {
  if (!docsUrl) return null;
  const match = String(docsUrl).match(/\/connectors\/([^/]+)\//);
  return match ? slugifyConnectorName(match[1]) : null;
}

function getConnectorSlug(connector) {
  return (
    slugFromDocsUrl(connector.docs_url) ||
    slugFromDocsUrl(connector.docsUrl) ||
    slugifyConnectorName(connector.connector_name)
  );
}

function getPlatformAvailabilityState(connector) {
  return connector.platform_availability?.state || PLATFORM_ENABLED;
}

function isEnabledConnector(connector) {
  const state = getPlatformAvailabilityState(connector);
  return state === PLATFORM_ENABLED;
}

function discoverAgentConnectorSlugs(
  connectorsDir = AGENT_CONNECTORS_DOCS_DIR,
) {
  try {
    return fs
      .readdirSync(connectorsDir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort();
  } catch (error) {
    console.warn("Could not read agent connectors directory:", error.message);
    return [];
  }
}

function extractEnabledAgentConnectorSlugs(registry, availableSlugs = null) {
  const availableSlugSet = availableSlugs ? new Set(availableSlugs) : null;
  const connectors = Array.isArray(registry?.connectors)
    ? registry.connectors
    : [];

  return connectors
    .filter(isEnabledConnector)
    .map(getConnectorSlug)
    .filter(Boolean)
    .filter((slug) => !availableSlugSet || availableSlugSet.has(slug))
    .sort();
}

async function fetchAgentConnectorAvailability() {
  console.log("Fetching agent connector availability...");
  const registry = await fetchJsonFromUrl(AGENT_CONNECTORS_REGISTRY_URL);
  const availableSlugs = discoverAgentConnectorSlugs();
  const enabledSlugs = extractEnabledAgentConnectorSlugs(
    registry,
    availableSlugs,
  );
  const enabledSet = new Set(enabledSlugs);
  const hiddenSlugs = availableSlugs.filter((slug) => !enabledSet.has(slug));

  console.log(
    `Found ${enabledSlugs.length} enabled agent connectors ` +
      `and ${hiddenSlugs.length} hidden connector docs`,
  );

  if (hiddenSlugs.length > 0) {
    console.log(`Hidden agent connector docs: ${hiddenSlugs.join(", ")}`);
  }

  return enabledSlugs;
}

function writeAgentConnectorAvailability(slugs) {
  const dir = path.dirname(AGENT_CONNECTORS_ENABLED_CACHE_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(
    AGENT_CONNECTORS_ENABLED_CACHE_PATH,
    `${JSON.stringify(slugs, null, 2)}\n`,
  );
}

async function prepareAgentConnectorAvailability() {
  const slugs = await fetchAgentConnectorAvailability();
  writeAgentConnectorAvailability(slugs);
  return slugs;
}

function loadEnabledAgentConnectorSlugs() {
  try {
    return JSON.parse(
      fs.readFileSync(AGENT_CONNECTORS_ENABLED_CACHE_PATH, "utf8"),
    );
  } catch (error) {
    console.warn(
      "Could not load agent connector availability data:",
      error.message,
    );
    return [];
  }
}

function filterEnabledAgentConnectorSlugs(slugs) {
  const enabledSlugs = new Set(loadEnabledAgentConnectorSlugs());
  return slugs.filter((slug) => enabledSlugs.has(slug)).sort();
}

module.exports = {
  PLATFORM_ENABLED,
  discoverAgentConnectorSlugs,
  extractEnabledAgentConnectorSlugs,
  fetchAgentConnectorAvailability,
  filterEnabledAgentConnectorSlugs,
  getConnectorSlug,
  isEnabledConnector,
  loadEnabledAgentConnectorSlugs,
  prepareAgentConnectorAvailability,
  slugifyConnectorName,
  writeAgentConnectorAvailability,
};
