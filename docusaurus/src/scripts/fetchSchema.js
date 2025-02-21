/**
 * This script downloads the declarative component schema from the airbyte-python-cdk repository.
 * 
 * Previously, the schema was imported directly from a local path:
 * import schema from "../../../airbyte-cdk/python/airbyte_cdk/sources/declarative/declarative_component_schema.yaml"
 * 
 * However, since the CDK has been moved to a separate repository (airbyte-python-cdk),
 * we now need to fetch the schema at build time. This script:
 * 1. Downloads the latest schema from the main branch
 * 2. Saves it to src/data/declarative_component_schema.yaml
 * 3. This local copy is then imported by ManifestYamlDefinitions.jsx and reference.md
 * 
 * The script runs automatically before both development (pnpm start) and build (pnpm build) commands.
 */

const fs = require('fs');
const https = require('https');
const path = require('path');

const SCHEMA_URL = 'https://raw.githubusercontent.com/airbytehq/airbyte-python-cdk/refs/heads/main/airbyte_cdk/sources/declarative/declarative_component_schema.yaml';
const OUTPUT_PATH = path.join(__dirname, '..', 'data', 'declarative_component_schema.yaml');

// Ensure the data directory exists
fs.mkdirSync(path.join(__dirname, '..', 'data'), { recursive: true });

https.get(SCHEMA_URL, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    fs.writeFileSync(OUTPUT_PATH, data);
    console.log('Schema file downloaded successfully');
  });
}).on('error', (err) => {
  console.error('Error downloading schema:', err);
  process.exit(1);
}); 