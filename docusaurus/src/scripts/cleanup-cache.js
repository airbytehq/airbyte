/**
 * This script cleans up the temporary registry cache file after the build is complete.
 * The cache file is generated during the prebuild phase and should not be
 * committed to git since it's regenerated on each build.
 */
const fs = require("fs");
const { REGISTRY_CACHE_PATH } = require("./constants");

function cleanupCache() {
  if (fs.existsSync(REGISTRY_CACHE_PATH)) {
    try {
      fs.unlinkSync(REGISTRY_CACHE_PATH);
      console.log(`Cleaned up cache file: ${REGISTRY_CACHE_PATH}`);
    } catch (error) {
      console.warn(`Failed to clean up ${REGISTRY_CACHE_PATH}:`, error.message);
    }
  }
}

cleanupCache();
