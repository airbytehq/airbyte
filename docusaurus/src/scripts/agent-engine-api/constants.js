/**
 * Shared constants for the Docusaurus documentation build process
 * 
 * This file contains paths and configuration values that are used across
 * multiple scripts and configuration files.
 */

const path = require("path");

// Get the project root directory (docusaurus folder)
const PROJECT_ROOT = path.resolve(__dirname, "..", "..", "..");

// Path to the cached Agent Engine API OpenAPI specification
const SPEC_CACHE_PATH = path.join(PROJECT_ROOT, "src", "data", "agent_engine_api_spec.json");

// URL for fetching the latest Agent Engine API specification
const AGENT_ENGINE_API_SPEC_URL = "https://airbyte-sonar-prod.s3.us-east-2.amazonaws.com/openapi/latest/app.json";

// API documentation output directory (relative to project root)
const API_DOCS_OUTPUT_DIR = "../docs/ai-agents/api/api-reference";

// Sidebar file path for generated API docs
const API_SIDEBAR_PATH = path.join(PROJECT_ROOT, API_DOCS_OUTPUT_DIR, "sidebar.ts");

module.exports = {
  PROJECT_ROOT,
  SPEC_CACHE_PATH,
  AGENT_ENGINE_API_SPEC_URL,
  API_DOCS_OUTPUT_DIR,
  API_SIDEBAR_PATH,
};
