/**
 * Utility to manage connector registry - fetching, caching, and extracting minimal data.
 *
 * Fetches the composite connector registry from the CDN and projects each entry
 * into the `_oss` / `_cloud` suffixed shape that the rest of the docs code
 * (remark plugins, sidebar, ConnectorRegistry.jsx) expects.
 *
 * The composite registry is a server-side superset of the OSS and Cloud
 * registries, keyed by definitionId (cloud preferred when present), and
 * exposes an `availability` field indicating which registries each connector
 * appears in.
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
 * Project a single composite registry entry into the `_oss` / `_cloud`
 * suffixed shape used by downstream consumers.
 *
 * Because the composite registry has one entry per definitionId (cloud
 * preferred when present), independent OSS vs Cloud field values cannot be
 * recovered here. Every `<field>_oss` and `<field>_cloud` pair is populated
 * with the same value from the composite entry; callers already handle the
 * `is_oss === false` / `is_cloud === false` cases via fallbacks.
 */
function buildCompositeEntry(entry, connectorType) {
  const dockerRepository = entry.dockerRepository || "";
  const connectorName = dockerRepository.replace("airbyte/", "");
  const definitionId =
    entry.sourceDefinitionId || entry.destinationDefinitionId || "";
  const availability = entry.availability || [];
  const isOss = availability.includes("oss");
  const isCloud = availability.includes("cloud");

  const githubUrl = `https://github.com/${GITHUB_REPO_NAME}/blob/master/${CONNECTORS_PATH}/${connectorName}`;
  const issuesLabel = `connectors/${connectorType}/${connectorName.replace(`${connectorType}-`, "")}`;
  const issueUrl = `https://github.com/${GITHUB_REPO_NAME}/issues?q=is:open+is:issue+label:${issuesLabel}`;

  return {
    connector_type: connectorType,
    definitionId,
    is_oss: isOss,
    is_cloud: isCloud,
    github_url: githubUrl,
    issue_url: issueUrl,

    // OSS fields — sourced from the composite entry (cloud-preferred when both exist)
    name_oss: entry.name || "",
    dockerRepository_oss: dockerRepository,
    dockerImageTag_oss: entry.dockerImageTag || "",
    supportLevel_oss: entry.supportLevel || "community",
    iconUrl_oss: entry.iconUrl || "",
    documentationUrl_oss: entry.documentationUrl || "",
    spec_oss: entry.spec || null,
    remoteRegistries_oss: entry.remoteRegistries || {},
    packageInfo_oss: entry.packageInfo || null,
    generated_oss: entry.generated || null,

    // Cloud fields — same composite entry values
    name_cloud: entry.name || "",
    dockerRepository_cloud: dockerRepository,
    dockerImageTag_cloud: entry.dockerImageTag || "",
    supportLevel_cloud: entry.supportLevel || "",
    documentationUrl_cloud: entry.documentationUrl || "",
    packageInfo_cloud: entry.packageInfo || null,
    generated_cloud: entry.generated || null,
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
    id: (connector.name_oss || connector.name_cloud)
      ?.toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, ""),
    // Properties used by sidebar-connectors.js
    docUrl:
      connector.documentationUrl_cloud || connector.documentationUrl_oss || "",
    supportLevel:
      connector.supportLevel_cloud || connector.supportLevel_oss || "community",
    // Properties used by remark/utils.js and remark/specDecoration.js
    dockerRepository_oss: connector.dockerRepository_oss || "",
    spec_oss: connector.spec_oss
      ? {
          connectionSpecification: connector.spec_oss.connectionSpecification,
        }
      : null,
    // Properties used by remark/utils.js for buildArchivedRegistryEntry
    name_oss: connector.name_oss || connector.name || "",
    is_oss: connector.is_oss || false,
    is_cloud: connector.is_cloud || false,
    iconUrl_oss: connector.iconUrl_oss || "",
    supportLevel_oss: connector.supportLevel_oss || "community",
    documentationUrl_oss: connector.documentationUrl_oss || "",
    // Properties used by remark/connectorList.js (isPypiConnector)
    remoteRegistries_oss: connector.remoteRegistries_oss || {},
    // Properties used by remark/docsHeaderDecoration.js for HeaderDecoration component
    dockerImageTag_oss: connector.dockerImageTag_oss || "",
    github_url: connector.github_url || "",
    issue_url: connector.issue_url || "",
    definitionId: connector.definitionId || "",
    packageInfo_oss: connector.packageInfo_oss || null,
    packageInfo_cloud: connector.packageInfo_cloud || null,
    generated_oss: connector.generated_oss || null,
    generated_cloud: connector.generated_cloud || null,
    // Properties used by ConnectorRegistry.jsx (client-side catalog page)
    connector_type: connector.connector_type || "",
    dockerRepository_cloud: connector.dockerRepository_cloud || "",
    dockerImageTag_cloud: connector.dockerImageTag_cloud || "",
    supportLevel_cloud: connector.supportLevel_cloud || "",
    documentationUrl_cloud: connector.documentationUrl_cloud || "",
    name_cloud: connector.name_cloud || "",
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
