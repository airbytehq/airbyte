/**
 * Test dereferencing logic on the actual spec
 */

const https = require("https");
const yaml = require("js-yaml");
const fs = require("fs");
const path = require("path");

const SOURCE_SPEC_URL =
  "https://raw.githubusercontent.com/airbytehq/airbyte-platform/refs/heads/main/airbyte-api/server-api/src/main/openapi/api_documentation_sources.yaml";

function fetchSpec(url) {
  return new Promise((resolve, reject) => {
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

/**
 * Simplified dereferencing for testing
 */
function dereferenceSchema(schema, schemas, visitedRefs = new Set(), depth = 0, maxDepth = 10) {
  if (depth > maxDepth) {
    console.log(`  [DEPTH LIMIT] at depth ${depth}`);
    return schema;
  }

  if (!schema || typeof schema !== "object") {
    return schema;
  }

  // Handle $ref
  if (schema.$ref && typeof schema.$ref === "string") {
    const refName = schema.$ref.split("/").pop();

    if (visitedRefs.has(refName)) {
      console.log(`  [CIRCULAR] keeping $ref to ${refName} (already visited)`);
      return schema;
    }

    if (schemas[refName]) {
      visitedRefs.add(refName);
      const resolved = dereferenceSchema(
        JSON.parse(JSON.stringify(schemas[refName])),
        schemas,
        visitedRefs,
        depth + 1,
        maxDepth
      );
      visitedRefs.delete(refName);
      // Remove $ref since we've dereferenced it
      const { $ref, ...schemaWithoutRef } = schema;
      return { ...schemaWithoutRef, ...resolved };
    }
    return schema;
  }

  // Make a shallow copy
  const result = Array.isArray(schema) ? [...schema] : { ...schema };

  // Process oneOf
  if (result.oneOf && Array.isArray(result.oneOf)) {
    result.oneOf = result.oneOf.map((item, idx) => {
      const deref = dereferenceSchema(item, schemas, new Set(visitedRefs), depth + 1, maxDepth);
      if (item.$ref && !deref.$ref) {
        // Successfully dereferenced
        return deref;
      } else if (item.$ref && deref.$ref) {
        // Still has $ref (circular or not found)
        return deref;
      }
      return deref;
    });
  }

  return result;
}

async function main() {
  try {
    console.log("Fetching spec...");
    const spec = await fetchSpec(SOURCE_SPEC_URL);
    console.log("✅ Spec fetched\n");

    const sourceConfig = spec.components.schemas.SourceConfiguration;
    const schemas = spec.components.schemas;

    console.log("=== DEREFERENCING TEST ===\n");
    console.log("SourceConfiguration before:");
    console.log(`  - oneOf length: ${sourceConfig.oneOf.length}`);
    console.log(`  - First item: ${JSON.stringify(sourceConfig.oneOf[0])}`);

    console.log("\nDereferencing SourceConfiguration...");
    const deref = dereferenceSchema(sourceConfig, schemas);

    console.log("\nSourceConfiguration after:");
    console.log(`  - oneOf length: ${deref.oneOf.length}`);
    console.log(`  - First item has $ref: ${!!deref.oneOf[0].$ref}`);
    console.log(`  - First item has properties: ${!!deref.oneOf[0].properties}`);
    console.log(`  - First item keys: ${Object.keys(deref.oneOf[0]).join(", ")}`);

    if (deref.oneOf[0].properties) {
      console.log(`  - First item properties: ${Object.keys(deref.oneOf[0].properties).join(", ").substring(0, 100)}`);
    }

    // Count dereferenced vs not
    const dereferenced = deref.oneOf.filter((item) => !item.$ref).length;
    const notDereferenced = deref.oneOf.filter((item) => item.$ref).length;

    console.log(`\nResults:`);
    console.log(`  - Dereferenced: ${dereferenced}`);
    console.log(`  - Still have $ref: ${notDereferenced}`);

    // Save result for inspection
    const output = path.join(__dirname, "../../data/test_deref_result.json");
    fs.mkdirSync(path.dirname(output), { recursive: true });

    // Only save first 3 oneOf items to keep file small
    const sampleResult = {
      ...deref,
      oneOf: deref.oneOf.slice(0, 3),
    };

    fs.writeFileSync(output, JSON.stringify(sampleResult, null, 2));
    console.log(`\n✅ Sample saved to: ${output}`);
  } catch (error) {
    console.error("❌ Error:", error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

main();
