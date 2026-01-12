/**
 * Test script to debug SourceConfiguration dereferencing
 * This reads only api_documentation_sources.yaml to understand the structure
 */

const https = require("https");
const yaml = require("js-yaml");
const fs = require("fs");
const path = require("path");

const SOURCE_SPEC_URL =
  "https://raw.githubusercontent.com/airbytehq/airbyte-platform/refs/heads/main/airbyte-api/server-api/src/main/openapi/api_documentation_sources.yaml";

/**
 * Fetches a spec from a URL
 */
function fetchSpec(url) {
  return new Promise((resolve, reject) => {
    console.log(`Fetching from ${url}...`);

    https
      .get(url, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Failed to fetch spec: ${response.statusCode}`));
          return;
        }

        let data = "";
        response.on("data", (chunk) => {
          data += chunk;
        });

        response.on("end", () => {
          try {
            const isYaml = url.endsWith(".yaml") || url.endsWith(".yml");
            if (isYaml) {
              const spec = yaml.load(data);
              resolve(spec);
            } else {
              const spec = JSON.parse(data);
              resolve(spec);
            }
          } catch (error) {
            reject(
              new Error(
                `Failed to parse spec data: ${
                  error instanceof Error ? error.message : String(error)
                }`
              )
            );
          }
        });
      })
      .on("error", (error) => {
        reject(new Error(`Network error: ${error.message}`));
      });
  });
}

async function main() {
  try {
    console.log("📥 Fetching api_documentation_sources.yaml...\n");
    const spec = await fetchSpec(SOURCE_SPEC_URL);

    console.log("✅ Spec fetched successfully\n");

    // Check SourceConfiguration
    const sourceConfig = spec.components?.schemas?.SourceConfiguration;

    if (!sourceConfig) {
      console.error("❌ SourceConfiguration not found in spec");
      return;
    }

    console.log("=== ANALYZING SourceConfiguration ===\n");
    console.log("Structure:");
    console.log("  - Type:", sourceConfig.type);
    console.log("  - Has description:", !!sourceConfig.description);
    console.log("  - Has oneOf:", !!sourceConfig.oneOf);
    console.log("  - Has anyOf:", !!sourceConfig.anyOf);
    console.log("  - Has allOf:", !!sourceConfig.allOf);
    console.log("  - Has $ref:", !!sourceConfig.$ref);
    console.log("  - Keys:", Object.keys(sourceConfig).join(", "));

    if (sourceConfig.oneOf) {
      console.log("\noneOf Array:");
      console.log("  - Length:", sourceConfig.oneOf.length);
      console.log("  - First item:", JSON.stringify(sourceConfig.oneOf[0], null, 2).substring(0, 300));
      console.log("  - First item has $ref:", !!sourceConfig.oneOf[0].$ref);
      console.log("  - First item has properties:", !!sourceConfig.oneOf[0].properties);
    }

    // Check if source schemas exist
    console.log("\nSource Schemas in components.schemas:");
    const schemaNames = Object.keys(spec.components?.schemas || {});
    const sourceSchemas = schemaNames.filter((name) => name.startsWith("source-"));
    console.log(`  - Total schemas: ${schemaNames.length}`);
    console.log(`  - Source schemas (source-*): ${sourceSchemas.length}`);
    if (sourceSchemas.length > 0) {
      console.log(`  - First source schema: ${sourceSchemas[0]}`);
      console.log(`  - Last source schema: ${sourceSchemas[sourceSchemas.length - 1]}`);
    }

    // Check one source schema
    if (sourceSchemas.length > 0) {
      const firstSource = spec.components.schemas[sourceSchemas[0]];
      console.log(`\nAnalyzing ${sourceSchemas[0]}:`);
      console.log(`  - Type: ${firstSource.type}`);
      console.log(`  - Has properties: ${!!firstSource.properties}`);
      console.log(`  - Has $ref: ${!!firstSource.$ref}`);
      console.log(`  - Keys: ${Object.keys(firstSource).join(", ")}`);
      if (firstSource.properties) {
        console.log(`  - Properties keys: ${Object.keys(firstSource.properties).join(", ").substring(0, 100)}`);
      }
    }

    // Write the raw spec to a test file to inspect
    const testOutput = path.join(__dirname, "../../data/test_sources_spec.json");
    fs.mkdirSync(path.dirname(testOutput), { recursive: true });
    fs.writeFileSync(testOutput, JSON.stringify(spec, null, 2));
    console.log(`\n✅ Full spec saved to: ${testOutput}`);
  } catch (error) {
    console.error("❌ Error:", error instanceof Error ? error.message : String(error));
  }
}

main();
