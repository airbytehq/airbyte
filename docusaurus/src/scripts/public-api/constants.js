/**
 * Shared constants for the Public API documentation build process
 *
 * This file contains paths and configuration values that are used across
 * multiple scripts for the public API documentation infrastructure.
 */

const path = require("path");


// Get the project root directory (docusaurus folder)
const PROJECT_ROOT = path.resolve(__dirname, "..", "..", "..");

// Path to the cached public API OpenAPI specification
const PUBLIC_API_SPEC_CACHE_PATH = path.join(
  PROJECT_ROOT,
  "src",
  "data",
  "public_api_spec.json",
);

// URL for fetching the latest public API specification
const PUBLIC_API_SPEC_URL =
  "https://raw.githubusercontent.com/airbytehq/airbyte-platform/refs/heads/main/airbyte-api/server-api/src/main/openapi/public_api.yaml";

// URL for fetching the configuration API specification (which contains tags)
const CONFIG_API_SPEC_URL =
  "https://raw.githubusercontent.com/airbytehq/airbyte-platform/refs/heads/main/airbyte-api/server-api/src/main/openapi/config.yaml";

// API documentation output directory (relative to project root)
const PUBLIC_API_DOCS_OUTPUT_DIR = "../docs/developers/api-reference";

// Sidebar file path for generated API docs
const PUBLIC_API_SIDEBAR_PATH = path.join(
  PROJECT_ROOT,
  PUBLIC_API_DOCS_OUTPUT_DIR,
  "sidebar.ts",
);

module.exports = {
  PROJECT_ROOT,
  PUBLIC_API_SPEC_CACHE_PATH,
  PUBLIC_API_SPEC_URL,
  CONFIG_API_SPEC_URL,
  PUBLIC_API_DOCS_OUTPUT_DIR,
  PUBLIC_API_SIDEBAR_PATH,
};
