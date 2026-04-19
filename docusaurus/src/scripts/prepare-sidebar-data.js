/**
 * This script ensures the connector registry cache exists and is populated.
 * It's called during the prebuild phase to prepare data for the build process.
 *
 * The cache is used by:
 * - remark/specDecoration.js - needs: dockerRepository, spec.connectionSpecification
 * - remark/connectorList.js - needs: remoteRegistries for isPypiConnector filter
 * - remark/utils.js - needs: dockerRepository, name, is_oss, is_cloud,
 *                     iconUrl, supportLevel, documentationUrl
 * - sidebar-connectors.js - needs: docUrl, supportLevel, dockerRepository
 *
 * This avoids network timeouts during the build process by fetching data once upfront.
 * The cache file is cleaned up after the build completes (see cleanup-cache.js).
 */
const { fetchRegistry } = require("./fetch-registry");

async function main() {
  try {
    await fetchRegistry();
  } catch (error) {
    console.error("Error preparing registry cache:", error);
    process.exit(1);
  }
}

main();
