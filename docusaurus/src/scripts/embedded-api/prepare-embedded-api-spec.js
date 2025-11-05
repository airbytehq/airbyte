/**
 * This script fetches the embedded API OpenAPI spec and processes it before
 * the build process starts. It ensures the spec is available and validated
 * for both the OpenAPI plugin and sidebar generation.
 */
const fs = require("fs");
const https = require("https");
const path = require("path");
const { validateOpenAPISpec } = require("./openapi-validator");
const { SPEC_CACHE_PATH, EMBEDDED_API_SPEC_URL } = require("./constants");

function fetchEmbeddedApiSpec() {
  return new Promise((resolve, reject) => {
    console.log("Fetching embedded API spec...");

    https
      .get(EMBEDDED_API_SPEC_URL, (response) => {
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
            const spec = JSON.parse(data);
            resolve(spec);
          } catch (error) {
            reject(
              new Error(`Failed to parse spec data: ${error.message}`),
            );
          }
        });
      })
      .on("error", (error) => {
        reject(new Error(`Network error: ${error.message}`));
      });
  });
}

// validateSpec function is now handled by AJV validator
// This provides comprehensive OpenAPI 3.1 schema validation

function processSpec(spec) {
  // For now, return the spec as-is
  // In the future, we could add processing/transformations here if needed
  return spec;
}

function loadPreviousSpec() {
  try {
    if (fs.existsSync(SPEC_CACHE_PATH)) {
      const previousSpec = JSON.parse(fs.readFileSync(SPEC_CACHE_PATH, 'utf8'));
      console.log("📁 Found previous spec version:", previousSpec.info?.version || "unknown");
      return previousSpec;
    }
  } catch (error) {
    console.warn("⚠️  Could not load previous spec:", error.message);
  }
  return null;
}

async function main() {
  
  const previousSpec = loadPreviousSpec();
  try {
    console.log("🔄 Attempting to fetch latest embedded API spec...");
    const spec = await fetchEmbeddedApiSpec();
    
    // Validate using comprehensive OpenAPI schema validator
    const validatedSpec = await validateOpenAPISpec(spec);
    const processedSpec = processSpec(validatedSpec);

    // Ensure the data directory exists
    const dir = path.dirname(SPEC_CACHE_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(
      SPEC_CACHE_PATH,
      JSON.stringify(processedSpec, null, 2),
    );

    console.log(
      `✅ Embedded API spec processed and saved to ${SPEC_CACHE_PATH}`,
    );
    
    if (previousSpec && previousSpec.info?.version !== processedSpec.info?.version) {
      //TODO: we don't use versioning yet, so we should find another way to compare specs and output changes?
      console.log(`📝 Spec updated from ${previousSpec.info?.version} to ${processedSpec.info?.version}`);
    }
    
  } catch (error) {
    console.error("❌ Error fetching/processing latest spec:", error.message);
    
    if (previousSpec) {
      console.log("🔄 Using previous cached spec version to continue build...");
      console.log(`📋 Previous spec info: ${previousSpec.info?.title} v${previousSpec.info?.version}`);
      
      // Ensure the previous spec is still written to the expected location
      const dir = path.dirname(SPEC_CACHE_PATH);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      fs.writeFileSync(
        SPEC_CACHE_PATH,
        JSON.stringify(previousSpec, null, 2),
      );
      
      console.log("✅ Build will continue with previous spec version");
    } else {
      console.error("💥 No previous spec found and latest fetch failed");
      console.error("📝 Creating minimal fallback spec to allow build to continue");
      console.error("💡 Tip: Run this script successfully once to create an initial cache");
      
      // Create minimal valid OpenAPI spec that will result in empty docs
      const fallbackSpec = {
        openapi: "3.1.0",
        info: {
          title: "Embedded API (Unavailable)",
          version: "0.0.0",
          description: "The embedded API specification could not be fetched. Please check your network connection and try again."
        },
        paths: {},
        tags: [],
        components: {}
      };
      
      // Ensure the data directory exists
      const dir = path.dirname(SPEC_CACHE_PATH);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      // Cleanup is now handled by package.json scripts before doc generation

      fs.writeFileSync(
        SPEC_CACHE_PATH,
        JSON.stringify(fallbackSpec, null, 2),
      );
      
      console.log("✅ Build will continue with empty embedded API documentation");
    }
  }
}

main();