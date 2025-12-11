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
const {
  PUBLIC_API_SPEC_CACHE_PATH,
  PUBLIC_API_SPEC_BASE_URL,
  PUBLIC_SPEC_FILE_NAMES,
  CONFIG_API_SPEC_URL,
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
 * Main processing function
 */
async function main() {
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
    const allPromises = [
      ...publicSpecUrls.map((url) => fetchSpec(url)),
      fetchSpec(CONFIG_API_SPEC_URL),
    ];

    const allResults = await Promise.all(allPromises);

    // Last result is the config spec
    const configResult = allResults[allResults.length - 1];
    const publicSpecResults = allResults.slice(0, -1);

    // Merge all public API specs into one
    const publicSpecs = publicSpecResults.map((result) => result.spec);
    const publicSpec = mergeSpecs(publicSpecs);
    const configSpec = configResult.spec;

    console.log(
      `📦 Merged Public API spec with ${publicSpecs.length} components`
    );
    console.log(
      `📦 Config spec: ${configSpec.info?.title} v${configSpec.info?.version}`
    );

    // Dereference all $ref values in the merged spec
    console.log("🔗 Dereferencing schema references...");

    // Use custom dereferencing to handle circular references intelligently
    const dereferencedSpec = {
      ...publicSpec,
      components: {
        ...publicSpec.components,
        schemas: {},
      },
    };

    // Dereference each schema while tracking to prevent infinite loops
    const schemas = publicSpec.components?.schemas || {};
    for (const schemaName in schemas) {
      const beforeDeref = JSON.stringify(schemas[schemaName]);
      dereferencedSpec.components.schemas[schemaName] = dereferenceSchema(
        schemas[schemaName],
        schemas
      );
      const afterDeref = JSON.stringify(dereferencedSpec.components.schemas[schemaName]);

      // Debug SourceConfiguration specifically
      if (schemaName === "SourceConfiguration") {
        console.log("\n=== DEBUGGING SourceConfiguration ===");
        console.log("Before dereferencing:");
        console.log("  - Has oneOf:", !!schemas[schemaName].oneOf);
        console.log("  - oneOf length:", schemas[schemaName].oneOf?.length || 0);
        if (schemas[schemaName].oneOf?.length > 0) {
          console.log("  - First item:", JSON.stringify(schemas[schemaName].oneOf[0]).substring(0, 100));
        }
        console.log("\nAfter dereferencing:");
        console.log("  - Has oneOf:", !!dereferencedSpec.components.schemas[schemaName].oneOf);
        console.log("  - oneOf length:", dereferencedSpec.components.schemas[schemaName].oneOf?.length || 0);
        if (dereferencedSpec.components.schemas[schemaName].oneOf?.length > 0) {
          const firstItem = dereferencedSpec.components.schemas[schemaName].oneOf[0];
          console.log("  - First item has $ref:", !!firstItem.$ref);
          console.log("  - First item has properties:", !!firstItem.properties);
          console.log("  - First item keys:", Object.keys(firstItem).join(", "));
          if (firstItem.title) {
            console.log("  - First item title:", firstItem.title);
          }
        }
        console.log("=== END DEBUG ===\n");
      }
    }

    // Also dereference schemas in paths (for inline responses, etc)
    if (publicSpec.paths) {
      for (const pathName in publicSpec.paths) {
        const pathItem = publicSpec.paths[pathName];
        for (const method in pathItem) {
          const operation = pathItem[method];
          if (operation && typeof operation === "object") {
            if (operation.requestBody?.content) {
              for (const mediaType in operation.requestBody.content) {
                const schema = operation.requestBody.content[mediaType].schema;
                if (schema) {
                  operation.requestBody.content[mediaType].schema = dereferenceSchema(
                    schema,
                    schemas
                  );
                }
              }
            }
            if (operation.responses) {
              for (const statusCode in operation.responses) {
                const response = operation.responses[statusCode];
                if (response?.content) {
                  for (const mediaType in response.content) {
                    const schema = response.content[mediaType].schema;
                    if (schema) {
                      response.content[mediaType].schema = dereferenceSchema(
                        schema,
                        schemas
                      );
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

    // Copy over paths and other properties
    dereferencedSpec.paths = publicSpec.paths;

    console.log("✅ Schema references dereferenced successfully");

    // Inject tags from config spec into public spec
    const enhancedSpec = injectTagsFromConfigSpec(dereferencedSpec, configSpec);

    // Validate the enhanced spec
    const validatedSpec = await validateOpenAPISpec(enhancedSpec);
    const processedSpec = validatedSpec;

    // Ensure the data directory exists
    const dir = path.dirname(PUBLIC_API_SPEC_CACHE_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Write the cached spec as YAML
    const yamlString = yaml.dump(processedSpec, {
      lineWidth: -1,  // Prevent line wrapping
      noRefs: false,  // Allow $ref to work properly in YAML
      sortKeys: false // Preserve key order
    });

    fs.writeFileSync(PUBLIC_API_SPEC_YAML_PATH, yamlString);

    console.log(
      `✅ Public API spec processed and saved to ${PUBLIC_API_SPEC_YAML_PATH}`
    );

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
main().catch((error) => {
  console.error(
    "Fatal error:",
    error instanceof Error ? error.message : String(error)
  );
  process.exit(1);
});
