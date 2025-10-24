/**
 * This script fetches the connector registry data and caches only the properties
 * needed by the build process before the build starts.
 *
 * The cache is used by:
 * - connector_registry.js during MDX compilation for SpecSchema components
 *   Needs: dockerRepository_oss, spec_oss.connectionSpecification
 * - sidebar-connectors.js for building the sidebar navigation
 *   Needs: docUrl, supportLevel
 *
 * This avoids network timeouts during the build process by fetching data once upfront.
 * The cache file is cleaned up after the build completes (see cleanup-cache.js).
 */
const fs = require("fs");
const https = require("https");
const { DATA_DIR, REGISTRY_CACHE_PATH, REGISTRY_URL } = require("./constants");


function fetchConnectorRegistry() {
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
    // Properties used by sidebar-connectors.js
    docUrl: connector.documentationUrl_cloud || connector.documentationUrl_oss || "",
    supportLevel: connector.supportLevel_cloud || connector.supportLevel_oss || "community",
    // Properties used by connector_registry.js
    dockerRepository_oss: connector.dockerRepository_oss || "",
    spec_oss: connector.spec_oss ? {
      connectionSpecification: connector.spec_oss.connectionSpecification,
    } : null,
  }));
}

async function main() {
  try {
    const fullRegistry = await fetchConnectorRegistry();

    // Extract only the properties we need for the build
    const minimalRegistry = extractMinimalRegistryData(fullRegistry);

    // Ensure data directory exists
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }

    // Save the minimal registry cache for use during build
    fs.writeFileSync(
      REGISTRY_CACHE_PATH,
      JSON.stringify(minimalRegistry, null, 2),
    );
    console.log(
      `Connector registry cached (${minimalRegistry.length} connectors) to ${REGISTRY_CACHE_PATH}`,
    );
  } catch (error) {
    console.error("Error preparing registry cache:", error);
    process.exit(1);
  }
}

main();
