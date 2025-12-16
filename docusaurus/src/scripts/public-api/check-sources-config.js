/**
 * Check which YAML files have SourceConfiguration and what they contain
 */

const https = require("https");
const yaml = require("js-yaml");

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

const BASE_URL =
  "https://raw.githubusercontent.com/airbytehq/airbyte-platform/refs/heads/main/airbyte-api/server-api/src/main/openapi/";

function fetchSpec(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Failed to fetch: ${response.statusCode}`));
          return;
        }
        let data = "";
        response.on("data", (chunk) => {
          data += chunk;
        });
        response.on("end", () => {
          try {
            const spec = yaml.load(data);
            resolve(spec);
          } catch (error) {
            reject(error);
          }
        });
      })
      .on("error", reject);
  });
}

async function main() {
  console.log("Checking which files have SourceConfiguration...\n");

  for (const fileName of PUBLIC_SPEC_FILE_NAMES) {
    try {
      const url = BASE_URL + fileName;
      const spec = await fetchSpec(url);

      const sourceConfig = spec.components?.schemas?.SourceConfiguration;

      if (sourceConfig) {
        console.log(`✓ ${fileName}`);
        console.log(
          `  - Has oneOf: ${!!sourceConfig.oneOf} (${sourceConfig.oneOf?.length || 0} items)`
        );
        console.log(`  - Has properties: ${!!sourceConfig.properties}`);
        console.log(`  - Has $ref: ${!!sourceConfig.$ref}`);
        console.log(`  - Keys: ${Object.keys(sourceConfig).join(", ")}`);
        console.log("");
      }
    } catch (error) {
      console.log(`✗ ${fileName}: ${error instanceof Error ? error.message : error}`);
    }
  }
}

main();
