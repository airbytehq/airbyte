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
 * Recursively dereferences $ref values in a schema, tracking visited schemas by name to avoid infinite loops
 */
function dereferenceSchema(schema, schemas, visitedRefs = new Set(), depth = 0, maxDepth = 50) {
  if (depth > maxDepth) {
    return schema; // Prevent infinite recursion
  }

  if (!schema || typeof schema !== "object") {
    return schema;
  }

  // Handle $ref
  if (schema.$ref && typeof schema.$ref === "string") {
    const refName = schema.$ref.split("/").pop(); // Extract name from "#/components/schemas/Name"
    // Check if we've already started dereferencing this schema (circular reference)
    if (visitedRefs.has(refName)) {
      return schema; // Keep the $ref to break the circular dependency
    }

    if (schemas[refName]) {
      // Add to visited before dereferencing to prevent circular loops
      visitedRefs.add(refName);

      const resolved = dereferenceSchema(
        JSON.parse(JSON.stringify(schemas[refName])), // Deep clone to avoid object references
        schemas,
        visitedRefs,
        depth + 1,
        maxDepth
      );

      // Remove from visited after processing (for sibling branches)
      visitedRefs.delete(refName);

      // Merge the resolved schema with other properties from the original schema
      // but remove the $ref since we've now dereferenced it
      const { $ref, ...schemaWithoutRef } = schema;
      return { ...schemaWithoutRef, ...resolved };
    }
    return schema; // Ref not found, keep as-is
  }

  // Make a shallow copy of the object to avoid mutating original
  const result = Array.isArray(schema) ? [...schema] : { ...schema };

  // Recursively process arrays (like oneOf, anyOf, allOf)
  if (result.oneOf && Array.isArray(result.oneOf)) {
    result.oneOf = result.oneOf.map((item) =>
      dereferenceSchema(item, schemas, new Set(visitedRefs), depth + 1, maxDepth)
    );
  }
  if (result.anyOf && Array.isArray(result.anyOf)) {
    result.anyOf = result.anyOf.map((item) =>
      dereferenceSchema(item, schemas, new Set(visitedRefs), depth + 1, maxDepth)
    );
  }
  if (result.allOf && Array.isArray(result.allOf)) {
    result.allOf = result.allOf.map((item) =>
      dereferenceSchema(item, schemas, new Set(visitedRefs), depth + 1, maxDepth)
    );
  }
  if (result.items) {
    result.items = dereferenceSchema(result.items, schemas, new Set(visitedRefs), depth + 1, maxDepth);
  }
  if (result.properties && typeof result.properties === "object") {
    const newProps = {};
    for (const key in result.properties) {
      newProps[key] = dereferenceSchema(
        result.properties[key],
        schemas,
        new Set(visitedRefs),
        depth + 1,
        maxDepth
      );
    }
    result.properties = newProps;
  }
  if (result.additionalProperties && typeof result.additionalProperties === "object") {
    result.additionalProperties = dereferenceSchema(
      result.additionalProperties,
      schemas,
      new Set(visitedRefs),
      depth + 1,
      maxDepth
    );
  }

  return result;
}

/**
 * Creates tag definitions from the public spec operations that are missing from config,
 * and merges with config tags
 */
function injectTagsFromConfigSpec(publicSpec, configSpec) {
  console.log("Injecting tags from config spec into public spec...");

  if (!configSpec.tags || configSpec.tags.length === 0) {
    throw new Error("Config spec has no tags to inject into public spec");
  }

  // Find all tags used by operations in the public spec (only first/primary tag per operation)
  const usedTags = new Set();
  for (const pathItem of Object.values(publicSpec.paths || {})) {
    const httpMethods = [
      "get",
      "put",
      "post",
      "delete",
      "options",
      "head",
      "patch",
      "trace",
    ];

    for (const method of httpMethods) {
      const operation = pathItem[method];
      // Only use the first tag (primary tag) for each operation
      if (operation?.tags && Array.isArray(operation.tags) && operation.tags.length > 0) {
        usedTags.add(operation.tags[0]);
      }
    }
  }

  // Create a map of config tags by name
  const configTagsMap = {};
  configSpec.tags.forEach((tag) => {
    configTagsMap[tag.name] = tag;
  });

  // Build final tag list: use config tags where available, create default ones for missing tags
  const finalTags = [];
  const addedTagNames = new Set();

  // First, add config tags that are used in the public spec
  for (const tagName of usedTags) {
    if (configTagsMap[tagName]) {
      finalTags.push(configTagsMap[tagName]);
      addedTagNames.add(tagName);
    }
  }

  // Then, create default tag definitions for tags that are used but not in config
  for (const tagName of usedTags) {
    if (!addedTagNames.has(tagName)) {
      finalTags.push({
        name: tagName,
        description: `${tagName} operations`,
      });
      addedTagNames.add(tagName);
    }
  }

  console.log(
    `✅ Created ${finalTags.length} tag definitions (${addedTagNames.size} from operations, ${
      finalTags.length - addedTagNames.size
    } from config)`
  );

  // Create a new spec with injected tags
  const enhancedSpec = {
    ...publicSpec,
    tags: finalTags,
  };

  // Clean up: keep only the first tag for each operation to avoid duplicates in sidebar
  console.log("Cleaning up operations to keep only primary tags...");
  for (const pathItem of Object.values(enhancedSpec.paths || {})) {
    const httpMethods = [
      "get",
      "put",
      "post",
      "delete",
      "options",
      "head",
      "patch",
      "trace",
    ];

    for (const method of httpMethods) {
      const operation = pathItem[method];
      if (operation?.tags && Array.isArray(operation.tags) && operation.tags.length > 1) {
        // Keep only the first tag
        operation.tags = [operation.tags[0]];
      }
    }
  }

  return enhancedSpec;
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

    // Inject tags from config spec into public spec
    console.time("INJECT_TAGS");
    const enhancedSpec = injectTagsFromConfigSpec(specToUseFiltered, configSpec);
    console.timeEnd("INJECT_TAGS");

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
