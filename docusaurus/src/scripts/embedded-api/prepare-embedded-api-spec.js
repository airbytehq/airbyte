#!/usr/bin/env node

/**
 * Smart embedded API spec preparation script.
 *
 * This script:
 * 1. Fetches the latest embedded API OpenAPI spec from S3
 * 2. Validates it using comprehensive OpenAPI schema validation
 * 3. Intelligently decides whether to regenerate API docs based on spec changes
 * 4. Runs the API doc generation pipeline only if needed
 * 5. Provides fallback behavior if fetch fails
 *
 * Features:
 * - Smart change detection: only regenerates if spec actually changed
 * - Caching: uses previous spec if fetch fails
 * - Validation: ensures spec is valid OpenAPI 3.1
 * - Graceful degradation: allows build to continue even if fetch fails
 *
 * Usage:
 *   node prepare-embedded-api-spec.js
 *
 */

const fs = require("fs");
const https = require("https");
const path = require("path");
const { execSync } = require("child_process");
const { validateOpenAPISpec } = require("./openapi-validator");
const {
  SPEC_CACHE_PATH,
  API_SIDEBAR_PATH,
  EMBEDDED_API_SPEC_URL,
} = require("./constants");

function log(message) {
  console.log(message);
}

function logError(message) {
  console.error(message);
}

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
            reject(new Error(`Failed to parse spec data: ${error.message}`));
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

function loadPreviousSpec() {
  try {
    if (fs.existsSync(SPEC_CACHE_PATH)) {
      const previousSpec = JSON.parse(fs.readFileSync(SPEC_CACHE_PATH, "utf8"));
      console.log(
        "📁 Found previous spec version:",
        previousSpec.info?.version || "unknown",
      );
      return previousSpec;
    }
  } catch (error) {
    console.warn("⚠️  Could not load previous spec:", error.message);
  }
  return null;
}

// ============================================================================
// Smart Detection & Regeneration
// ============================================================================

/**
 * Check if generated API documentation files exist and are valid
 */
function generatedFilesMissing() {
  try {
    const sidebarPath = API_SIDEBAR_PATH;
    const sidebarExists = fs.existsSync(sidebarPath);

    if (!sidebarExists) {
      log("✅ Generated files missing (sidebar.ts not found), regenerating...");
      return true;
    }

    const apiDocsDir = path.dirname(sidebarPath);
    const dirExists = fs.existsSync(apiDocsDir);

    if (!dirExists) {
      log("✅ API docs directory missing, regenerating...");
      return true;
    }

    const files = fs
      .readdirSync(apiDocsDir)
      .filter((f) => f !== ".gitignore" && f !== "README.txt");
    if (files.length === 0) {
      log("✅ API docs directory is empty, regenerating...");
      return true;
    }

    log(`ℹ️  Generated files present (${files.length} files found)`);
    return false;
  } catch (e) {
    logError("⚠️  Error checking generated files, defaulting to regenerate");
    return true;
  }
}

/**
 * Determine if regeneration is needed by comparing specs
 */
function shouldRegenerateApiDocs(newSpec, previousSpec) {
  if (generatedFilesMissing()) {
    return true;
  }

  if (!previousSpec) {
    log("✅ No previous spec found, regenerating...");
    return true;
  }

  // Compare specs by converting to JSON strings
  const newJson = JSON.stringify(newSpec, null, 2);
  const previousJson = JSON.stringify(previousSpec, null, 2);

  if (newJson === previousJson) {
    log("✅ Spec unchanged, skipping API docs regeneration");
    return false;
  }

  log("✅ Spec changed, regenerating API docs...");
  return true;
}

/**
 * Regenerate API documentation
 */
function regenerateApiDocs() {
  try {
    log("⚙️  Running API doc generation pipeline...");

    // Run the docusaurus commands
    execSync("pnpm exec docusaurus clean-api-docs all", { stdio: "inherit" });
    execSync("pnpm exec docusaurus gen-api-docs all", { stdio: "inherit" });

    log("✅ API docs regeneration completed successfully");
    return true;
  } catch (e) {
    logError("❌ Failed to regenerate API docs");
    logError(`   Error: ${e.message}`);
    return false;
  }
}

async function main() {
  const startTime = Date.now();
  log("[prepare-embedded-api] Starting script...");

  const previousSpec = loadPreviousSpec();
  try {
    log("🔄 Attempting to fetch latest embedded API spec...");
    const spec = await fetchEmbeddedApiSpec();

    // Validate using comprehensive OpenAPI schema validator
    const validatedSpec = await validateOpenAPISpec(spec);

    // Ensure the data directory exists
    const dir = path.dirname(SPEC_CACHE_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(SPEC_CACHE_PATH, JSON.stringify(validatedSpec, null, 2));

    log(`✅ Embedded API spec processed and saved to ${SPEC_CACHE_PATH}`);

    // Smart detection: decide if we need to regenerate API docs
    log("");
    log("🔍 Checking if API docs regeneration is needed...");
    const shouldRegen = shouldRegenerateApiDocs(validatedSpec, previousSpec);

    if (shouldRegen) {
      log("📝 API docs will be regenerated");
      log("");

      const success = regenerateApiDocs();

      if (!success) {
        logError("");
        logError("⚠️  API docs regeneration failed, but build will continue");
      }
      log("");
      const duration = Date.now() - startTime;
      log(`[prepare-embedded-api] ✅ Completed in ${duration}ms`);
      process.exit(0);
    } else {
      log("✅ API docs regeneration skipped - no changes detected");
      log("");
      const duration = Date.now() - startTime;
      log(`[prepare-embedded-api] ✅ Completed in ${duration}ms`);
      process.exit(0);
    }
  } catch (error) {
    logError("❌ Error fetching/processing latest spec:", error.message);

    if (previousSpec) {
      log("🔄 Using previous cached spec version to continue build...");
      log(
        `📋 Previous spec info: ${previousSpec.info?.title} v${previousSpec.info?.version}`,
      );

      // Ensure the previous spec is still written to the expected location
      const dir = path.dirname(SPEC_CACHE_PATH);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      fs.writeFileSync(SPEC_CACHE_PATH, JSON.stringify(previousSpec, null, 2));

      log("✅ Build will continue with previous spec version");
      log("");
      const duration = Date.now() - startTime;
      log(
        `[prepare-embedded-api] ⚠️  Completed in ${duration}ms (used cached spec)`,
      );
      process.exit(0);
    } else {
      logError("💥 No previous spec found and latest fetch failed");
      logError("📝 Creating minimal fallback spec to allow build to continue");
      logError(
        "💡 Tip: Run this script successfully once to create an initial cache",
      );

      // Create minimal valid OpenAPI spec that will result in empty docs
      const fallbackSpec = {
        openapi: "3.1.0",
        info: {
          title: "Embedded API (Unavailable)",
          version: "0.0.0",
          description:
            "The embedded API specification could not be fetched. Please check your network connection and try again.",
        },
        paths: {},
        tags: [],
        components: {},
      };

      // Ensure the data directory exists
      const dir = path.dirname(SPEC_CACHE_PATH);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      fs.writeFileSync(SPEC_CACHE_PATH, JSON.stringify(fallbackSpec, null, 2));

      log("✅ Build will continue with empty embedded API documentation");
      log("");
      const duration = Date.now() - startTime;
      log(
        `[prepare-embedded-api] ⚠️  Completed in ${duration}ms (fallback spec)`,
      );
      process.exit(0);
    }
  }
}

main();
