/**
 * This script fetches the embedded API OpenAPI spec and processes it before
 * the build process starts. It ensures the spec is available and validated
 * for both the OpenAPI plugin and sidebar generation.
 */
const fs = require("fs");
const https = require("https");
const path = require("path");

const SPEC_CACHE_PATH = path.join(
  __dirname,
  "..",
  "data",
  "embedded_api_spec.json",
);

const SPEC_URL =
  "https://airbyte-sonar-prod.s3.us-east-2.amazonaws.com/openapi/latest/app.json";

function fetchEmbeddedApiSpec() {
  return new Promise((resolve, reject) => {
    console.log("Fetching embedded API spec...");

    https
      .get(SPEC_URL, (response) => {
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

function validateSpec(spec) {
  // Basic validation to ensure spec has required structure
  if (!spec || typeof spec !== "object") {
    throw new Error("Invalid spec: not an object");
  }

  if (!spec.info || !spec.info.title) {
    throw new Error("Invalid spec: missing info.title");
  }

  if (!spec.tags || !Array.isArray(spec.tags)) {
    throw new Error("Invalid spec: missing or invalid tags array");
  }

  if (!spec.paths || typeof spec.paths !== "object") {
    throw new Error("Invalid spec: missing or invalid paths");
  }

  // Log some useful info
  console.log(`Spec title: ${spec.info.title}`);
  console.log(`Spec version: ${spec.info.version || "unknown"}`);
  console.log(`Found ${spec.tags.length} tags`);
  console.log(`Found ${Object.keys(spec.paths).length} paths`);

  return spec;
}

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
    
    const validatedSpec = validateSpec(spec);
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
      console.error("💥 No previous spec found and latest fetch failed - cannot continue");
      console.error("💡 Tip: Run this script successfully once to create an initial cache");
      process.exit(1);
    }
  }
}

main();