/**
 * This script fetches the public API OpenAPI spec and the config API spec,
 * injects the tags from config into public API, and caches the result.
 *
 * The public API spec lacks a top-level tags array, but the Airbyte Configuration API
 * (which the public API is a subset of) has comprehensive tags with display names.
 * This script merges the tags from the config spec into the public spec.
 */

const fs = require("fs");
const https = require("https");
const path = require("path");
const yaml = require("js-yaml");
const RefParser = require("json-schema-ref-parser");
const { validateOpenAPISpec } = require("./openapi-validator");
const { fetchRegistry } = require("../fetch-registry");
const {
  PUBLIC_API_SPEC_CACHE_PATH,
  PUBLIC_API_SPEC_BASE_URL,
  PUBLIC_SPEC_FILE_NAMES,
  CONFIG_API_SPEC_URL,
  SOURCE_CONFIGS_DEREFERENCED_PATH,
  PUBLIC_API_TAGS_PATH,
} = require("./constants");

// Create a YAML version of the cache path
const PUBLIC_API_SPEC_YAML_PATH = PUBLIC_API_SPEC_CACHE_PATH.replace(".json", ".yaml");

/**
 * Fetches an OpenAPI spec from a URL
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
            // Determine format from URL
            const isYaml = url.endsWith(".yaml") || url.endsWith(".yml");

            if (isYaml) {
              // Parse YAML
              const spec = yaml.load(data);
              resolve({
                spec,
                format: "yaml",
                url,
              });
            } else {
              // Parse JSON
              const spec = JSON.parse(data);
              resolve({
                spec,
                format: "json",
                url,
              });
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

/**
 * Loads the previous cached spec if it exists
 */
function loadPreviousSpec() {
  try {
    if (fs.existsSync(PUBLIC_API_SPEC_CACHE_PATH)) {
      const previousSpec = JSON.parse(
        fs.readFileSync(PUBLIC_API_SPEC_CACHE_PATH, "utf8")
      );
      console.log(
        "📁 Found previous spec version:",
        previousSpec.info?.version || "unknown"
      );
      return previousSpec;
    }
  } catch (error) {
    console.warn(
      "⚠️  Could not load previous spec:",
      error instanceof Error ? error.message : String(error)
    );
  }
  return null;
}

/**
 * Merges multiple OpenAPI specs into a single spec
 */
function mergeSpecs(specs) {
  if (specs.length === 0) {
    throw new Error("No specs provided to merge");
  }

  const baseSpec = specs[0];
  const merged = {
    ...baseSpec,
    paths: { ...baseSpec.paths },
    components: {
      schemas: { ...baseSpec.components?.schemas },
      ...baseSpec.components,
    },
  };

  // Merge all paths and schemas from remaining specs
  for (let i = 1; i < specs.length; i++) {
    const spec = specs[i];

    if (spec.paths) {
      Object.assign(merged.paths, spec.paths);
    }

    if (spec.components?.schemas) {
      // Merge schemas intelligently - don't overwrite fuller schemas with stub versions
      for (const schemaName in spec.components.schemas) {
        const newSchema = spec.components.schemas[schemaName];
        const existingSchema = merged.components.schemas[schemaName];

        if (existingSchema) {
          // Count properties to determine which is more complete
          const existingKeys = Object.keys(existingSchema).length;
          const newKeys = Object.keys(newSchema).length;

          // Keep the schema with more properties/content
          if (newKeys > existingKeys) {
            merged.components.schemas[schemaName] = newSchema;
          }
          // Otherwise keep the existing one
        } else {
          // Schema doesn't exist yet, add it
          merged.components.schemas[schemaName] = newSchema;
        }
      }
    }
  }

  console.log(
    `✅ Merged ${specs.length} spec files into single spec with ${
      Object.keys(merged.paths).length
    } paths`
  );

  return merged;
}

/**
 * Mapping from operation path + method to the new display tag.
 * Built from the curated tag mapping spreadsheet.
 * Operations not in this mapping will be excluded from the docs.
 */
const OPERATION_TAG_MAPPING = {
  "GET /applications": "Applications",
  "POST /applications": "Applications",
  "POST /applications/token": "Applications",
  "DELETE /applications/{applicationId}": "Applications",
  "GET /applications/{applicationId}": "Applications",
  "GET /connections": "Connections and streams",
  "POST /connections": "Connections and streams",
  "DELETE /connections/{connectionId}": "Connections and streams",
  "GET /connections/{connectionId}": "Connections and streams",
  "PATCH /connections/{connectionId}": "Connections and streams",
  "GET /connector_definitions": "Connections and streams",
  "GET /dataplanes": "Data planes",
  "POST /dataplanes": "Data planes",
  "DELETE /dataplanes/{dataplaneId}": "Data planes",
  "GET /dataplanes/{dataplaneId}": "Data planes",
  "PATCH /dataplanes/{dataplaneId}": "Data planes",
  "GET /destinations": "Connectors",
  "POST /destinations": "Connectors",
  "DELETE /destinations/{destinationId}": "Connectors",
  "GET /destinations/{destinationId}": "Connectors",
  "PATCH /destinations/{destinationId}": "Connectors",
  "PUT /destinations/{destinationId}": "Connectors",
  "GET /groups": "Groups",
  "POST /groups": "Groups",
  "DELETE /groups/{groupId}": "Groups",
  "GET /groups/{groupId}": "Groups",
  "PATCH /groups/{groupId}": "Groups",
  "GET /groups/{groupId}/members": "Groups",
  "POST /groups/{groupId}/members": "Groups",
  "DELETE /groups/{groupId}/members/{userId}": "Groups",
  "GET /groups/{groupId}/permissions": "Groups",
  "POST /groups/{groupId}/permissions": "Groups",
  "DELETE /groups/{groupId}/permissions/{permissionId}": "Groups",
  "GET /health": "Health",
  "GET /jobs": "Jobs",
  "POST /jobs": "Jobs",
  "DELETE /jobs/{jobId}": "Jobs",
  "GET /jobs/{jobId}": "Jobs",
  "GET /oauth/callback": "OAuth",
  "GET /organizations": "Organizations and workspaces",
  "PUT /organizations/{organizationId}/oauthCredentials": "OAuth",
  "GET /permissions": "Permissions",
  "POST /permissions": "Permissions",
  "DELETE /permissions/{permissionId}": "Permissions",
  "GET /permissions/{permissionId}": "Permissions",
  "PATCH /permissions/{permissionId}": "Permissions",
  "GET /regions": "Regions",
  "POST /regions": "Regions",
  "DELETE /regions/{regionId}": "Regions",
  "GET /regions/{regionId}": "Regions",
  "PATCH /regions/{regionId}": "Regions",
  "GET /sources": "Connectors",
  "POST /sources": "Connectors",
  "POST /sources/initiateOAuth": "OAuth",
  "DELETE /sources/{sourceId}": "Connectors",
  "GET /sources/{sourceId}": "Connectors",
  "PATCH /sources/{sourceId}": "Connectors",
  "PUT /sources/{sourceId}": "Connectors",
  "GET /streams": "Connections and streams",
  "GET /tags": "Tags",
  "POST /tags": "Tags",
  "DELETE /tags/{tagId}": "Tags",
  "GET /tags/{tagId}": "Tags",
  "PATCH /tags/{tagId}": "Tags",
  "GET /users": "Users",
  "GET /workspaces": "Organizations and workspaces",
  "POST /workspaces": "Organizations and workspaces",
  "DELETE /workspaces/{workspaceId}": "Organizations and workspaces",
  "GET /workspaces/{workspaceId}": "Organizations and workspaces",
  "PATCH /workspaces/{workspaceId}": "Organizations and workspaces",
  "GET /workspaces/{workspaceId}/definitions/declarative_sources": "Declarative connector definitions",
  "POST /workspaces/{workspaceId}/definitions/declarative_sources": "Declarative connector definitions",
  "DELETE /workspaces/{workspaceId}/definitions/declarative_sources/{definitionId}": "Declarative connector definitions",
  "GET /workspaces/{workspaceId}/definitions/declarative_sources/{definitionId}": "Declarative connector definitions",
  "PUT /workspaces/{workspaceId}/definitions/declarative_sources/{definitionId}": "Declarative connector definitions",
  "GET /workspaces/{workspaceId}/definitions/destinations": "Connector definitions",
  "POST /workspaces/{workspaceId}/definitions/destinations": "Connector definitions",
  "DELETE /workspaces/{workspaceId}/definitions/destinations/{definitionId}": "Connector definitions",
  "GET /workspaces/{workspaceId}/definitions/destinations/{definitionId}": "Connector definitions",
  "PUT /workspaces/{workspaceId}/definitions/destinations/{definitionId}": "Connector definitions",
  "GET /workspaces/{workspaceId}/definitions/sources": "Connector definitions",
  "POST /workspaces/{workspaceId}/definitions/sources": "Connector definitions",
  "DELETE /workspaces/{workspaceId}/definitions/sources/{definitionId}": "Connector definitions",
  "GET /workspaces/{workspaceId}/definitions/sources/{definitionId}": "Connector definitions",
  "PUT /workspaces/{workspaceId}/definitions/sources/{definitionId}": "Connector definitions",
  "PUT /workspaces/{workspaceId}/oauthCredentials": "OAuth",
};

/**
 * Applies tags from the curated public_api_tags.json file to the spec.
 * - Loads tag definitions (name + description) from the JSON file
 * - Rewrites each operation's tags to use the new display tag as the primary tag
 * - Removes operations that are not in the curated mapping (not public)
 */
function applyTagsFromFile(publicSpec) {
  console.log("Applying tags from public_api_tags.json...");

  // Load curated tags from file
  const tagsFromFile = JSON.parse(fs.readFileSync(PUBLIC_API_TAGS_PATH, "utf-8"));
  const allowedTagNames = new Set(tagsFromFile.map((t) => t.name));

  console.log(`   📋 Loaded ${tagsFromFile.length} curated tags: ${[...allowedTagNames].join(", ")}`);

  const httpMethods = ["get", "put", "post", "delete", "options", "head", "patch", "trace"];

  // Rewrite operation tags and remove non-public endpoints
  const filteredPaths = {};
  let includedCount = 0;
  let excludedCount = 0;

  for (const [pathKey, pathItem] of Object.entries(publicSpec.paths || {})) {
    const filteredPathItem = {};
    let hasOperations = false;

    for (const method of httpMethods) {
      const operation = pathItem[method];
      if (!operation) continue;

      // Build the lookup key: "METHOD /path"
      const lookupKey = `${method.toUpperCase()} ${pathKey}`;
      const newTag = OPERATION_TAG_MAPPING[lookupKey];

      if (newTag && allowedTagNames.has(newTag)) {
        // Rewrite tags: new display tag as the only tag
        operation.tags = [newTag];
        filteredPathItem[method] = operation;
        hasOperations = true;
        includedCount++;
      } else {
        excludedCount++;
      }
    }

    // Copy over non-method properties (parameters, etc.)
    if (hasOperations) {
      for (const [key, value] of Object.entries(pathItem)) {
        if (!httpMethods.includes(key) && !(key in filteredPathItem)) {
          filteredPathItem[key] = value;
        }
      }
      filteredPaths[pathKey] = filteredPathItem;
    }
  }

  console.log(`   ✅ Included ${includedCount} operations, excluded ${excludedCount} non-public operations`);

  // Only include tags that actually have operations
  const usedTagNames = new Set();
  for (const pathItem of Object.values(filteredPaths)) {
    for (const method of httpMethods) {
      const operation = pathItem[method];
      if (operation?.tags) {
        operation.tags.forEach((t) => usedTagNames.add(t));
      }
    }
  }

  const finalTags = tagsFromFile.filter((t) => usedTagNames.has(t.name));
  console.log(`   📊 ${finalTags.length} tags have operations: ${finalTags.map((t) => t.name).join(", ")}`);

  return {
    ...publicSpec,
    paths: filteredPaths,
    tags: finalTags,
  };
}

/**
 * Extracts certified source names from the connector registry
 * @param {Array} registry - The connector registry from fetchRegistry()
 * @returns {Set<string>} Set of certified source names (e.g., "source-airtable")
 */
function extractCertifiedSourceNames(registry) {
  const certifiedSources = registry
    .filter(connector =>
      connector.supportLevel === 'certified' &&
      connector.dockerRepository_oss &&
      connector.dockerRepository_oss.includes('source-')
    )
    .map(connector => connector.dockerRepository_oss.replace('airbyte/', ''));

  return new Set(certifiedSources);
}

/**
 * Filters SourceConfiguration.oneOf to include only certified connectors
 * @param {Object} spec - The OpenAPI specification
 * @param {Set<string>} certifiedSourceNames - Set of certified source names
 * @returns {Object} The modified spec with filtered SourceConfiguration
 */
function filterSourceConfigurationToCertified(spec, certifiedSourceNames) {
  // Guard clause: check if SourceConfiguration exists
  if (!spec.components?.schemas?.SourceConfiguration?.oneOf) {
    console.warn('⚠️  SourceConfiguration.oneOf not found in spec - skipping filtering');
    return spec;
  }

  const sourceConfig = spec.components.schemas.SourceConfiguration;
  const originalCount = sourceConfig.oneOf.length;

  // Filter to only certified sources
  sourceConfig.oneOf = sourceConfig.oneOf.filter(item =>
    item.title && certifiedSourceNames.has(item.title)
  );

  const filteredCount = sourceConfig.oneOf.length;

  console.log(`✅ Filtered SourceConfiguration.oneOf: ${originalCount} → ${filteredCount} certified sources`);

  return spec;
}

/**
 * Recursively dereference a schema by resolving all $ref pointers
 * @param {Object} schema - The schema to dereference
 * @param {Object} allSchemas - All available schemas for reference resolution
 * @param {Set<string>} visited - Track visited schemas to avoid infinite loops
 * @returns {Object} The dereferenced schema
 */
function dereferenceSchema(schema, allSchemas, visited = new Set()) {
  if (!schema || typeof schema !== 'object' || Array.isArray(schema)) {
    return schema;
  }

  // Handle $ref pointers
  if (schema.$ref) {
    const refPath = schema.$ref;
    const schemaName = refPath.split('/').pop(); // Extract name from "#/components/schemas/source-postgres"

    // Prevent infinite loops
    if (visited.has(schemaName)) {
      return schema; // Return as-is if we've already visited
    }

    visited.add(schemaName);

    const referencedSchema = allSchemas[schemaName];
    if (!referencedSchema) {
      console.warn(`⚠️  Could not find schema: ${schemaName}`);
      return schema;
    }

    // Recursively dereference the referenced schema
    return dereferenceSchema(referencedSchema, allSchemas, new Set(visited));
  }

  // Recursively process nested objects
  const dereferenced = {};
  for (const [key, value] of Object.entries(schema)) {
    if (value && typeof value === 'object') {
      if (Array.isArray(value)) {
        dereferenced[key] = value.map(item =>
          typeof item === 'object' ? dereferenceSchema(item, allSchemas, visited) : item
        );
      } else {
        dereferenced[key] = dereferenceSchema(value, allSchemas, new Set(visited));
      }
    } else {
      dereferenced[key] = value;
    }
  }

  return dereferenced;
}

/**
 * Formats a source name for display
 * @param {string} name - The source name (e.g., "source-postgres")
 * @returns {string} Formatted name (e.g., "Postgres")
 */
function formatSourceName(name) {
  if (!name.startsWith('source-')) {
    return name;
  }

  // Remove "source-" prefix and convert to title case
  const withoutPrefix = name.substring(7); // Remove "source-"
  return withoutPrefix
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Extract and dereference all source schemas from SourceConfiguration
 * @param {Object} spec - The OpenAPI specification
 * @returns {Array} Array of source configs with dereferenced schemas
 */
function extractAndDereferenceSourceSchemas(spec) {
  if (!spec.components?.schemas?.SourceConfiguration?.oneOf) {
    console.warn('⚠️  SourceConfiguration.oneOf not found - skipping extraction');
    return [];
  }

  const sourceConfig = spec.components.schemas.SourceConfiguration;
  const allSchemas = spec.components.schemas;
  const sourceConfigs = [];

  console.log(`🔍 Extracting ${sourceConfig.oneOf.length} source configurations...`);

  for (const sourceRef of sourceConfig.oneOf) {
    if (!sourceRef.title) {
      console.warn('⚠️  Source config without title found, skipping');
      continue;
    }

    const sourceId = sourceRef.title; // e.g., "source-postgres"
    const sourceSchema = allSchemas[sourceId];

    if (!sourceSchema) {
      console.warn(`⚠️  Could not find schema for ${sourceId}`);
      continue;
    }

    try {
      // Dereference the schema
      const dereferenced = dereferenceSchema(sourceSchema, allSchemas);

      sourceConfigs.push({
        id: sourceId,
        displayName: formatSourceName(sourceId),
        schema: dereferenced
      });
    } catch (error) {
      console.warn(`⚠️  Error dereferencing ${sourceId}:`, error instanceof Error ? error.message : String(error));
    }
  }

  // Sort alphabetically by displayName
  sourceConfigs.sort((a, b) => a.displayName.localeCompare(b.displayName));

  console.log(`✅ Extracted and dereferenced ${sourceConfigs.length} source configurations`);

  return sourceConfigs;
}

/**
 * Main processing function
 */
async function main() {
  console.log("⏱️  [START] Prepare public API spec");
  console.time("TOTAL");

  const previousSpec = loadPreviousSpec();

  try {
    console.log(
      "🔄 Attempting to fetch latest public API and config specs..."
    );

    // Build URLs for all public spec files
    const publicSpecUrls = PUBLIC_SPEC_FILE_NAMES.map(
      (fileName) => `${PUBLIC_API_SPEC_BASE_URL}${fileName}`
    );

    console.log(
      `📥 Fetching ${PUBLIC_SPEC_FILE_NAMES.length} public API spec files and config spec...`
    );

    // Fetch all public spec files and config spec in parallel
    console.time("FETCH_SPECS");
    const allPromises = [
      ...publicSpecUrls.map((url) => fetchSpec(url)),
      fetchSpec(CONFIG_API_SPEC_URL),
    ];

    const allResults = await Promise.all(allPromises);
    console.timeEnd("FETCH_SPECS");

    // Last result is the config spec
    const configResult = allResults[allResults.length - 1];
    const publicSpecResults = allResults.slice(0, -1);

    // Merge all public API specs into one
    console.time("MERGE_SPECS");
    const publicSpecs = publicSpecResults.map((result) => result.spec);
    const publicSpec = mergeSpecs(publicSpecs);
    const configSpec = configResult.spec;
    console.timeEnd("MERGE_SPECS");

    // Override info.title to avoid collision with tag names
    // (the OpenAPI plugin generates both .info.mdx and .tag.mdx files,
    // and if info.title matches a tag name they get the same doc ID)
    publicSpec.info = {
      ...publicSpec.info,
      title: "Airbyte API",
    };

    console.log(
      `📦 Merged Public API spec with ${publicSpecs.length} components`
    );
    console.log(
      `📦 Config spec: ${configSpec.info?.title} v${configSpec.info?.version}`
    );

    // SKIP dereferencing for now - keep all $ref pointers intact
    // This allows us to get a working baseline to debug the Docusaurus build issue
    console.log("⏭️  Skipping dereferencing - keeping all $ref pointers intact");
    console.log("   Reason: Testing if dereferencing is causing the Docusaurus build to hang");

    // Use the publicSpec directly without any dereferencing
    console.log('✅ Using SourceConfiguration in spec');
    console.log('   docusaurus-plugin-llms-txt has been disabled');

    let specToUseFiltered = publicSpec;

    // Filter SourceConfiguration to certified connectors only
    try {
      const registry = await fetchRegistry();
      const certifiedSourceNames = extractCertifiedSourceNames(registry);
      console.log(`📦 Fetched registry with ${registry.length} connectors`);
      specToUseFiltered = filterSourceConfigurationToCertified(specToUseFiltered, certifiedSourceNames);
    } catch (error) {
      console.warn('⚠️  Could not filter to certified connectors:', error.message);
      console.log('   Using all SourceConfiguration items instead');
    }

    // Apply tags from curated public_api_tags.json and filter to public endpoints only
    console.time("APPLY_TAGS");
    const enhancedSpec = applyTagsFromFile(specToUseFiltered);
    console.timeEnd("APPLY_TAGS");

    // Validate the enhanced spec
    console.time("VALIDATE_SPEC");
    const validatedSpec = await validateOpenAPISpec(enhancedSpec);
    console.timeEnd("VALIDATE_SPEC");
    const processedSpec = validatedSpec;

    // Extract and dereference source schemas for the component
    console.time("EXTRACT_SCHEMAS");
    const sourceConfigsDeref = extractAndDereferenceSourceSchemas(processedSpec);
    console.timeEnd("EXTRACT_SCHEMAS");
    console.log(`   📊 Extracted ${sourceConfigsDeref.length} source configurations`);

    // Save dereferenced source configurations to JSON file
    if (sourceConfigsDeref.length > 0) {
      console.time("SAVE_JSON");
      const sourceConfigsJson = JSON.stringify(sourceConfigsDeref, null, 2);

      // Ensure the data directory exists
      const dataDir = path.dirname(SOURCE_CONFIGS_DEREFERENCED_PATH);
      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }

      fs.writeFileSync(SOURCE_CONFIGS_DEREFERENCED_PATH, sourceConfigsJson);
      console.timeEnd("SAVE_JSON");
      console.log(
        `✅ Source configurations extracted and saved to ${SOURCE_CONFIGS_DEREFERENCED_PATH}`
      );
      console.log(`   📦 JSON file size: ${(sourceConfigsJson.length / 1024).toFixed(2)} KB`);
    }

    // Ensure the data directory exists
    const dir = path.dirname(PUBLIC_API_SPEC_CACHE_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Write the cached spec as YAML
    console.time("DUMP_YAML");
    const yamlString = yaml.dump(processedSpec, {
      lineWidth: -1,  // Prevent line wrapping
      noRefs: false,  // Allow $ref to work properly in YAML
      sortKeys: false // Preserve key order
    });
    console.timeEnd("DUMP_YAML");

    console.time("WRITE_YAML");
    fs.writeFileSync(PUBLIC_API_SPEC_YAML_PATH, yamlString);
    console.timeEnd("WRITE_YAML");

    console.log(
      `✅ Public API spec processed and saved to ${PUBLIC_API_SPEC_YAML_PATH}`
    );
    console.log(`   📦 YAML file size: ${(yamlString.length / 1024 / 1024).toFixed(2)} MB`);

    if (
      previousSpec &&
      previousSpec.info?.version !== processedSpec.info?.version
    ) {
      console.log(
        `📝 Spec updated from ${previousSpec.info?.version} to ${processedSpec.info?.version}`
      );
    }
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : String(error);
    console.error("❌ Error fetching/processing latest spec:", errorMessage);

    if (previousSpec) {
      console.log(
        "🔄 Using previous cached spec version to continue build..."
      );
      console.log(
        `📋 Previous spec info: ${previousSpec.info?.title} v${previousSpec.info?.version}`
      );

      // Ensure the previous spec is still written to the expected location
      const dir = path.dirname(PUBLIC_API_SPEC_CACHE_PATH);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      const yamlString = yaml.dump(previousSpec, {
        lineWidth: -1,
        noRefs: false,
        sortKeys: false
      });
      fs.writeFileSync(PUBLIC_API_SPEC_YAML_PATH, yamlString);

      console.log("✅ Build will continue with previous spec version");
    } else {
      console.error("💥 No previous spec found and latest fetch failed");
      console.error(
        "📝 Creating minimal fallback spec to allow build to continue"
      );
      console.error(
        "💡 Tip: Run this script successfully once to create an initial cache"
      );

      // Create minimal valid OpenAPI spec that will result in empty docs
      const fallbackSpec = {
        openapi: "3.1.0",
        info: {
          title: "Public API (Unavailable)",
          version: "0.0.0",
          description:
            "The public API specification could not be fetched. Please check your network connection and try again.",
        },
        paths: {},
        tags: [],
        components: {},
      };

      // Ensure the data directory exists
      const dir = path.dirname(PUBLIC_API_SPEC_CACHE_PATH);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      const yamlString = yaml.dump(fallbackSpec, {
        lineWidth: -1,
        noRefs: false,
        sortKeys: false
      });
      fs.writeFileSync(PUBLIC_API_SPEC_YAML_PATH, yamlString);

      console.log("✅ Build will continue with empty public API documentation");
    }
  }
}

// Run the main function
main()
  .then(() => {
    console.timeEnd("TOTAL");
    console.log("⏱️  [COMPLETE] Prepare public API spec");
  })
  .catch((error) => {
    console.timeEnd("TOTAL");
    console.error(
      "Fatal error:",
      error instanceof Error ? error.message : String(error)
    );
    process.exit(1);
  });
