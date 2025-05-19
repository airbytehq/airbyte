/**
 * This script fetches the connector registry data and processes it before
 * the build process starts. It ensures the data is available for the sidebar
 * to use even on the first build.
 */
const fs = require("fs");
const https = require("https");
const path = require("path");
const REGISTRY_CACHE_PATH = path.join(
  __dirname,
  "..",
  "data",
  "connector_registry_slim.json",
);

const REGISTRY_URL =
  "https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json";

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

function processRegistryData(registry) {
  return registry
    .map((connector) => {
      const name = connector.name_oss || connector.name_cloud || "";
      if (name) {
        return {
          id: name
            .toLowerCase()
            .replace(/\s+/g, "-")
            .replace(/[^a-z0-9-]/g, ""),
          type: connector.connector_type?.toLowerCase() || "unknown",
          supportLevel:
            connector.supportLevel_cloud ||
            connector.supportLevel_oss ||
            "community",
          docUrl:
            connector.documentationUrl_cloud ||
            connector.documentationUrl_oss ||
            "",
        };
      }
    })
    .filter(Boolean);
}

async function main() {
  try {
    const registry = await fetchConnectorRegistry();

    const processedRegistry = processRegistryData(registry);

    const dir = path.dirname(REGISTRY_CACHE_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(
      REGISTRY_CACHE_PATH,
      JSON.stringify(processedRegistry, null, 2),
    );

    console.log(
      `Connector registry data processed and saved to ${REGISTRY_CACHE_PATH}`,
    );
  } catch (error) {
    console.error("Error preparing sidebar data:", error);
    process.exit(1);
  }
}

main();
