/**
 * Utility to manage connector registry - fetching, caching, and extracting minimal data.
 *
 * Fetches the composite connector registry from the CDN and projects each
 * entry into the flat shape that the rest of the docs code (remark plugins,
 * sidebar, ConnectorRegistry.jsx) consumes.
 *
 * The composite registry is a server-side superset of the OSS and Cloud
 * registries, keyed by definitionId (cloud preferred when present), and
 * exposes an `availability` field indicating which registries each connector
 * appears in — the only bit we carry through as separate `is_oss` / `is_cloud`
 * booleans.
 */
const fs = require("fs");
const https = require("https");
const { DATA_DIR, REGISTRY_CACHE_PATH, COMPOSITE_REGISTRY_URL } = require("./constants");

const GITHUB_REPO_NAME = "airbytehq/airbyte";
const CONNECTORS_PATH = "airbyte-integrations/connectors";

function fetchJsonFromUrl(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (response) => {
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
      })
      .on("error", (error) => {
        reject(new Error(`Network error fetching ${url}: ${error.message}`));
      });
  });
}

/**
 * Project a single composite registry entry into the shape used by downstream
 * consumers. The composite registry has one entry per definitionId (cloud
 * preferred when present), so we expose a single flat set of connector fields
 * plus `is_oss` / `is_cloud` availability booleans.
 */
function buildCompositeEntry(entry, connectorType) {
  const dockerRepository = entry.dockerRepository || "";
  const connectorName = dockerRepository.replace("airbyte/", "");
  const definitionId =
    entry.sourceDefinitionId || entry.destinationDefinitionId || "";
  const availability = entry.availability || [];

  const githubUrl = `https://github.com/${GITHUB_REPO_NAME}/blob/master/${CONNECTORS_PATH}/${connectorName}`;
  const issuesLabel = `connectors/${connectorType}/${connectorName.replace(`${connectorType}-`, "")}`;
  const issueUrl = `https://github.com/${GITHUB_REPO_NAME}/issues?q=is:open+is:issue+label:${issuesLabel}`;

  return {
    connector_type: connectorType,
    definitionId,
    is_oss: availability.includes("oss"),
    is_cloud: availability.includes("cloud"),
    github_url: githubUrl,
    issue_url: issueUrl,

    name: entry.name || "",
    dockerRepository,
    dockerImageTag: entry.dockerImageTag || "",
    supportLevel: entry.supportLevel || "community",
    iconUrl: entry.iconUrl || "",
    documentationUrl: entry.documentationUrl || "",
    spec: entry.spec || null,
    remoteRegistries: entry.remoteRegistries || {},
    packageInfo: entry.packageInfo || null,
    generated: entry.generated || null,
  };
}

async function fetchConnectorRegistriesFromRemote() {
  console.log("Fetching composite connector registry...");
  const compositeRegistry = await fetchJsonFromUrl(COMPOSITE_REGISTRY_URL);
  const sources = compositeRegistry.sources || [];
  const destinations = compositeRegistry.destinations || [];
  console.log(
    `Fetched ${sources.length + destinations.length} connectors ` +
      `(${sources.length} sources, ${destinations.length} destinations)`,
  );
  return [
    ...sources.map((entry) => buildCompositeEntry(entry, "source")),
    ...destinations.map((entry) => buildCompositeEntry(entry, "destination")),
  ];
}

function extractMinimalRegistryData(fullRegistry) {
  return fullRegistry.map((connector) => ({
    id: connector.name
      ?.toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, ""),
    // Properties used by sidebar-connectors.js
    docUrl: connector.documentationUrl || "",
    // Core connector fields (consumed by remark plugins, sidebar, the
    // client-side catalog page, etc.).
    connector_type: connector.connector_type || "",
    definitionId: connector.definitionId || "",
    is_oss: connector.is_oss || false,
    is_cloud: connector.is_cloud || false,
    github_url: connector.github_url || "",
    issue_url: connector.issue_url || "",
    name: connector.name || "",
    dockerRepository: connector.dockerRepository || "",
    dockerImageTag: connector.dockerImageTag || "",
    supportLevel: connector.supportLevel || "community",
    iconUrl: connector.iconUrl || "",
    documentationUrl: connector.documentationUrl || "",
    // Strip `spec` down to only the subset remark/specDecoration.js consumes
    // so the cached JSON stays small.
    spec: connector.spec
      ? { connectionSpecification: connector.spec.connectionSpecification }
      : null,
    remoteRegistries: connector.remoteRegistries || {},
    packageInfo: connector.packageInfo || null,
    generated: connector.generated || null,
  }));
}

async function fetchRegistry() {
  // Check if cache already exists
  if (fs.existsSync(REGISTRY_CACHE_PATH)) {
    const cachedData = fs.readFileSync(REGISTRY_CACHE_PATH, "utf8");
    const minimalRegistry = JSON.parse(cachedData);
    return minimalRegistry;
  }

  // Fetch both registries and merge if cache doesn't exist
  const fullRegistry = await fetchConnectorRegistriesFromRemote();
  const minimalRegistry = extractMinimalRegistryData(fullRegistry);

  // Ensure data directory exists
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  // Save the minimal registry cache
  fs.writeFileSync(
    REGISTRY_CACHE_PATH,
    JSON.stringify(minimalRegistry, null, 2),
  );
  console.log(`✓ Cached ${minimalRegistry.length} connectors`);

  return minimalRegistry;
}

module.exports = {
  fetchRegistry,
  fetchConnectorRegistriesFromRemote,
  extractMinimalRegistryData,
};
