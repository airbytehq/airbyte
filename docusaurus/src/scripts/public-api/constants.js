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

// Path to the dereferenced source configurations (extracted at build time)
const SOURCE_CONFIGS_DEREFERENCED_PATH = path.join(
  PROJECT_ROOT,
  "src",
  "data",
  "source-configs-dereferenced.json",
);

// URL for fetching the latest public API specification
const PUBLIC_API_SPEC_BASE_URL =
  "https://raw.githubusercontent.com/airbytehq/airbyte-platform/refs/heads/main/airbyte-api/server-api/src/main/openapi/";

const PUBLIC_SPEC_FILE_NAMES = [
  "api_documentation_applications.yaml",
  "api_documentation_config_templates.yaml",
  "api_documentation_connections.yaml",
  "api_documentation_declarative_source_definitions.yaml",
  "api_documentation_definitions.yaml",
  "api_documentation_destination_definitions.yaml",
  "api_documentation_destinations.yaml",
  "api_documentation_embedded_widget.yaml",
  "api_documentation_jobs.yaml",
  "api_documentation_organizations.yaml",
  "api_documentation_permissions.yaml",
  "api_documentation_source_definitions.yaml",
  "api_documentation_sources.yaml",
  "api_documentation_streams.yaml",
  "api_documentation_tags.yaml",
  "api_documentation_users.yaml",
  "api_documentation_workspaces.yaml",
];

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
  SOURCE_CONFIGS_DEREFERENCED_PATH,
  PUBLIC_API_SPEC_BASE_URL,
  PUBLIC_SPEC_FILE_NAMES,
  CONFIG_API_SPEC_URL,
  PUBLIC_API_DOCS_OUTPUT_DIR,
  PUBLIC_API_SIDEBAR_PATH,
};
