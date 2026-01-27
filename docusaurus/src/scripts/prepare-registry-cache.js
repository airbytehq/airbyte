/**
 * This script ensures the connector registry cache exists and is populated.
 * It's called during the prebuild phase to prepare data for the build process.
 *
 * The cache is used by:
 * - remark/specDecoration.js - needs: dockerRepository_oss, spec_oss.connectionSpecification
 * - remark/connectorList.js - needs: remoteRegistries_oss for isPypiConnector filter
 * - remark/utils.js - needs: dockerRepository_oss, name_oss, is_oss, is_cloud,
 *                     iconUrl_oss, supportLevel_oss, documentationUrl_oss
 * - sidebar-connectors.js - needs: docUrl, supportLevel, dockerRepository_oss
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
