const fs = require("fs");
const https = require("https");
const path = require("path");
const yaml = require("js-yaml");
const {
  validateOpenAPISpec,
} = require("../agent-engine-api/openapi-validator");
const { SPEC_CACHE_PATH, PUBLIC_API_SPEC_URL } = require("./constants");

const shouldSlimSpec = process.env.PUBLIC_API_SLIM !== "false";

function ensureTags(spec) {
  if (Array.isArray(spec.tags) && spec.tags.length > 0) {
    return spec;
  }

  const tagNames = new Set();
  for (const pathItem of Object.values(spec.paths || {})) {
    for (const method of [
      "get",
      "put",
      "post",
      "delete",
      "options",
      "head",
      "patch",
      "trace",
    ]) {
      for (const tag of pathItem?.[method]?.tags || []) {
        tagNames.add(tag);
      }
    }
  }

  spec.tags = [...tagNames].map((name) => ({ name }));
  return spec;
}

function fetchPublicApiSpec() {
  return new Promise((resolve, reject) => {
    console.log("Fetching public API spec...");

    https
      .get(PUBLIC_API_SPEC_URL, (response) => {
        if (response.statusCode !== 200) {
          response.resume();
          reject(new Error(`Failed to fetch spec: ${response.statusCode}`));
          return;
        }

        let data = "";
        response.setEncoding("utf8");
        response.on("data", (chunk) => {
          data += chunk;
        });
        response.on("end", () => {
          try {
            resolve(yaml.load(data));
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

function loadCachedSpec() {
  if (!fs.existsSync(SPEC_CACHE_PATH)) {
    return null;
  }

  try {
    return JSON.parse(fs.readFileSync(SPEC_CACHE_PATH, "utf8"));
  } catch (error) {
    console.warn(`Could not load cached public API spec: ${error.message}`);
    return null;
  }
}

function resolveJsonPointer(document, reference) {
  if (!reference.startsWith("#/")) {
    return null;
  }

  return reference
    .slice(2)
    .split("/")
    .map((part) => part.replace(/~1/g, "/").replace(/~0/g, "~"))
    .reduce((value, part) => value?.[part], document);
}

function pruneUnreachableSchemas(spec) {
  const schemas = spec.components?.schemas;
  if (!schemas) {
    return 0;
  }

  const reachableSchemas = new Set();
  const visitedReferences = new Set();

  function visit(value) {
    if (!value || typeof value !== "object") {
      return;
    }

    if (Array.isArray(value)) {
      value.forEach(visit);
      return;
    }

    if (typeof value.$ref === "string" && !visitedReferences.has(value.$ref)) {
      visitedReferences.add(value.$ref);
      const schemaMatch = value.$ref.match(/^#\/components\/schemas\/(.+)$/);
      if (schemaMatch) {
        reachableSchemas.add(
          decodeURIComponent(
            schemaMatch[1].replace(/~1/g, "/").replace(/~0/g, "~"),
          ),
        );
      }
      visit(resolveJsonPointer(spec, value.$ref));
    }

    Object.entries(value).forEach(([key, child]) => {
      if (key !== "$ref") {
        visit(child);
      }
    });
  }

  visit(spec.paths);

  const originalSchemaCount = Object.keys(schemas).length;
  spec.components.schemas = Object.fromEntries(
    Object.entries(schemas).filter(([name]) => reachableSchemas.has(name)),
  );

  return originalSchemaCount - Object.keys(spec.components.schemas).length;
}

function isConnectorConfigurationUnion(name, schema) {
  if (!Array.isArray(schema?.oneOf) || schema.oneOf.length < 20) {
    return false;
  }

  if (/^(Source|Destination).*Configuration/i.test(name)) {
    return true;
  }

  const references = schema.oneOf
    .map((variant) => variant?.$ref)
    .filter((reference) => typeof reference === "string");
  const connectorReferences = references.filter((reference) =>
    /#\/components\/schemas\/(?:source|destination)-/i.test(reference),
  );

  return (
    references.length === schema.oneOf.length &&
    connectorReferences.length / references.length >= 0.8
  );
}

function replaceConnectorConfigurationUnions(spec) {
  const schemas = spec.components?.schemas;
  if (!schemas) {
    return [];
  }

  const replacedSchemas = [];
  for (const [name, schema] of Object.entries(schemas)) {
    if (!isConnectorConfigurationUnion(name, schema)) {
      continue;
    }

    const connectorType = /^Source/i.test(name)
      ? "source"
      : /^Destination/i.test(name)
        ? "destination"
        : "source or destination";
    schemas[name] = {
      type: "object",
      additionalProperties: true,
      description:
        `The configuration shape depends on the ${connectorType} connector type. ` +
        "See the connector documentation for the fields supported by each connector: " +
        "[connector documentation](/integrations/).",
    };
    replacedSchemas.push(name);
  }

  return replacedSchemas;
}

function processSpec(spec) {
  if (!shouldSlimSpec) {
    console.log("PUBLIC_API_SLIM=false; keeping the full public API spec");
    return spec;
  }

  const replacedSchemas = replaceConnectorConfigurationUnions(spec);
  const prunedSchemaCount = pruneUnreachableSchemas(spec);
  console.log(
    `Slimmed public API spec: replaced ${replacedSchemas.length} connector ` +
      `configuration unions and pruned ${prunedSchemaCount} unreachable schemas`,
  );
  return spec;
}

function writeSpec(spec) {
  const directory = path.dirname(SPEC_CACHE_PATH);
  fs.mkdirSync(directory, { recursive: true });
  fs.writeFileSync(SPEC_CACHE_PATH, `${JSON.stringify(spec, null, 2)}\n`);
}

async function main() {
  let spec;
  try {
    spec = await fetchPublicApiSpec();
    spec = ensureTags(spec);
    spec = await validateOpenAPISpec(spec);
    spec = processSpec(spec);
    await validateOpenAPISpec(spec);
    writeSpec(spec);
    console.log(`Public API spec saved to ${SPEC_CACHE_PATH}`);
  } catch (error) {
    console.error(
      `Error fetching/processing latest public API spec: ${error.message}`,
    );
    spec = loadCachedSpec();
    if (!spec) {
      throw new Error("No cached public API spec is available", {
        cause: error,
      });
    }
    console.log("Using the committed cached public API spec");
    writeSpec(spec);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
