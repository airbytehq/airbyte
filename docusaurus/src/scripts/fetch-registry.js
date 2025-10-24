/**
 * Utility to manage connector registry - fetching, caching, and extracting minimal data.
 * This is a separate utility so it can be reused by multiple scripts.
 */
const fs = require("fs");
const https = require("https");
const { DATA_DIR, REGISTRY_CACHE_PATH, REGISTRY_URL } = require("./constants");

function fetchConnectorRegistryFromRemote() {
  return new Promise((resolve, reject) => {
    console.log("Fetching connector registry data...");

    https
      .get(REGISTRY_URL, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Failed to fetch registry: ${response.statusCode}`));
          return;
        }

        let data = "";

        response.on("data", (chunk) => {
          data += chunk;
        });

        response.on("end", () => {
          try {
            const registry = JSON.parse(data);
            resolve(registry);
          } catch (error) {
            reject(
              new Error(`Failed to parse registry data: ${error.message}`),
            );
          }
        });
      })
      .on("error", (error) => {
        reject(new Error(`Network error: ${error.message}`));
      });
  });
}

function extractMinimalRegistryData(fullRegistry) {
  return fullRegistry.map((connector) => ({
    id: connector.name_oss || connector.name_cloud
      .toLowerCase()
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
  }));
}

async function fetchRegistry() {
  // Check if cache already exists
  if (fs.existsSync(REGISTRY_CACHE_PATH)) {
    const cachedData = fs.readFileSync(REGISTRY_CACHE_PATH, "utf8");
    const minimalRegistry = JSON.parse(cachedData);
    return minimalRegistry;
  }

  // Fetch if cache doesn't exist
  const fullRegistry = await fetchConnectorRegistryFromRemote();
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
  fetchConnectorRegistryFromRemote,
  extractMinimalRegistryData,
};
