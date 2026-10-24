const path = require("path");

const PROJECT_ROOT = path.resolve(__dirname, "..", "..", "..");
const SPEC_CACHE_PATH = path.join(
  PROJECT_ROOT,
  "src",
  "data",
  "public_api_spec.json",
);
const PUBLIC_API_SPEC_URL =
  "https://raw.githubusercontent.com/airbytehq/airbyte-platform/master/airbyte-api/server-api/src/main/openapi/api_sdk.yaml";
const API_DOCS_OUTPUT_DIR = "../docs/developers/api-reference";
const API_SIDEBAR_PATH = path.join(
  PROJECT_ROOT,
  API_DOCS_OUTPUT_DIR,
  "sidebar.ts",
);

module.exports = {
  PROJECT_ROOT,
  SPEC_CACHE_PATH,
  PUBLIC_API_SPEC_URL,
  API_DOCS_OUTPUT_DIR,
  API_SIDEBAR_PATH,
};
