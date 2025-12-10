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
const { validateOpenAPISpec } = require("./openapi-validator");
const {
  PUBLIC_API_SPEC_CACHE_PATH,
  PUBLIC_API_SPEC_URL,
  CONFIG_API_SPEC_URL,
} = require("./constants");

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
 * Creates tag definitions from the public spec operations that are missing from config,
 * and merges with config tags
 */
function injectTagsFromConfigSpec(publicSpec, configSpec) {
  console.log("Injecting tags from config spec into public spec...");

  if (!configSpec.tags || configSpec.tags.length === 0) {
    throw new Error("Config spec has no tags to inject into public spec");
  }

  // Find all tags used by operations in the public spec
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
      if (operation?.tags && Array.isArray(operation.tags)) {
        operation.tags.forEach((tag) => {
          usedTags.add(tag);
        });
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

    // Fetch both specs in parallel
    const [publicApiResult, configResult] = await Promise.all([
      fetchSpec(PUBLIC_API_SPEC_URL),
      fetchSpec(CONFIG_API_SPEC_URL),
    ]);

    const publicSpec = publicApiResult.spec;
    const configSpec = configResult.spec;

    console.log(
      `📦 Public API spec: ${publicSpec.info?.title} v${publicSpec.info?.version}`
    );
    console.log(
      `📦 Config spec: ${configSpec.info?.title} v${configSpec.info?.version}`
    );

    // Inject tags from config spec into public spec
    const enhancedSpec = injectTagsFromConfigSpec(publicSpec, configSpec);

    // Validate the enhanced spec
    const validatedSpec = await validateOpenAPISpec(enhancedSpec);
    const processedSpec = validatedSpec;

    // Ensure the data directory exists
    const dir = path.dirname(PUBLIC_API_SPEC_CACHE_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Write the cached spec
    fs.writeFileSync(
      PUBLIC_API_SPEC_CACHE_PATH,
      JSON.stringify(processedSpec, null, 2)
    );

    console.log(
      `✅ Public API spec processed and saved to ${PUBLIC_API_SPEC_CACHE_PATH}`
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

      fs.writeFileSync(
        PUBLIC_API_SPEC_CACHE_PATH,
        JSON.stringify(previousSpec, null, 2)
      );

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

      fs.writeFileSync(
        PUBLIC_API_SPEC_CACHE_PATH,
        JSON.stringify(fallbackSpec, null, 2)
      );

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
