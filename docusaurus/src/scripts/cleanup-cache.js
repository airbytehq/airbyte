/**
 * This script cleans up the temporary registry cache file after the build is complete.
 * The cache file is generated during the prebuild phase and should not be
 * committed to git since it's regenerated on each build.
 */
const fs = require("fs");
const { REGISTRY_CACHE_PATH, AGENT_CONNECTOR_MANIFEST_PATH } = require("./constants");

function cleanupFile(filePath) {
  if (fs.existsSync(filePath)) {
    try {
      fs.unlinkSync(filePath);
      console.log(`Cleaned up cache file: ${filePath}`);
    } catch (error) {
      console.warn(`Failed to clean up ${filePath}:`, error.message);
    }
  }
}

function cleanupCache() {
  cleanupFile(REGISTRY_CACHE_PATH);
  cleanupFile(AGENT_CONNECTOR_MANIFEST_PATH);
}

cleanupCache();
