async function validateOpenAPISpec(spec) {
  console.log(
    "Validating OpenAPI spec with @seriousme/openapi-schema-validator...",
  );

  let Validator;
  try {
    ({ Validator } = await import("@seriousme/openapi-schema-validator"));
  } catch (error) {
    console.warn(
      "Could not load OpenAPI schema validator, using basic validation:",
      error.message,
    );
    return performBasicValidation(spec);
  }

  const validator = new Validator();
  const result = await validator.validate(spec);

  if (!result.valid) {
    const errors = Array.isArray(result.errors)
      ? result.errors
          .map((error) => {
            const path = error.instancePath || error.schemaPath || "unknown";
            return `  • ${path}: ${error.message || "validation failed"}`;
          })
          .join("\n")
      : String(result.errors || "Unknown validation errors");
    throw new Error(`OpenAPI spec validation failed:\n${errors}`);
  }

  const validatedSpec = validator.specification;
  validateDocumentationSpec(validatedSpec);
  console.log("OpenAPI spec validation passed");
  logValidationStats(validatedSpec);
  return validatedSpec;
}

function validateDocumentationSpec(spec) {
  if (!Array.isArray(spec.tags) || spec.tags.length === 0) {
    throw new Error(
      "OpenAPI spec must have tags array (required for sidebar generation)",
    );
  }

  const definedTags = new Set(spec.tags.map((tag) => tag.name));
  const usedTags = new Set();
  const criticalIssues = [];
  let operationsWithIssues = 0;

  for (const [path, pathItem] of Object.entries(spec.paths || {})) {
    for (const method of OPENAPI_METHODS) {
      const operation = pathItem[method];
      if (!operation) {
        continue;
      }

      operation.tags?.forEach((tag) => usedTags.add(tag));
      const operationRef = `${path}[${method.toUpperCase()}]`;

      if (!operation.operationId) {
        criticalIssues.push(
          `${operationRef} missing operationId (required for MDX file generation)`,
        );
      }
      if (!operation.tags?.length) {
        criticalIssues.push(
          `${operationRef} missing tags (required for sidebar grouping)`,
        );
      }
      if (
        !operation.responses ||
        Object.keys(operation.responses).length === 0
      ) {
        criticalIssues.push(
          `${operationRef} missing responses (required for documentation)`,
        );
      }
      if (!operation.summary) {
        console.warn(
          `${operationRef} missing summary (recommended for UI display)`,
        );
        operationsWithIssues++;
      }

      const responseCodes = Object.keys(operation.responses || {});
      if (
        responseCodes.length > 0 &&
        !responseCodes.some(
          (code) => code.startsWith("2") || code === "default",
        )
      ) {
        console.warn(
          `${operationRef} has no success response (2xx or default)`,
        );
      }
    }
  }

  const unusedTags = [...definedTags].filter((tag) => !usedTags.has(tag));
  if (unusedTags.length > 0) {
    throw new Error(
      `Defined tags have no operations and will not appear in docs: ${unusedTags.join(", ")}`,
    );
  }

  const undefinedTags = [...usedTags].filter((tag) => !definedTags.has(tag));
  if (undefinedTags.length > 0) {
    console.warn(
      `Operations reference undefined tags (will be uncategorized): ${undefinedTags.join(", ")}`,
    );
  }

  if (criticalIssues.length > 0) {
    throw new Error(
      `Critical OpenAPI documentation issues found:\n${criticalIssues.map((issue) => `  • ${issue}`).join("\n")}`,
    );
  }

  if (operationsWithIssues > 0) {
    console.warn(
      `Found ${operationsWithIssues} operation(s) with potential documentation issues`,
    );
  }
}

function performBasicValidation(spec) {
  if (!spec || typeof spec !== "object") {
    throw new Error("Invalid spec: not an object");
  }
  if (!spec.openapi && !spec.swagger) {
    throw new Error("Invalid spec: missing openapi or swagger version field");
  }
  if (!spec.info?.title || !spec.info.version) {
    throw new Error("Invalid spec: missing info.title or info.version");
  }
  if (!spec.paths || typeof spec.paths !== "object") {
    throw new Error("Invalid spec: missing or invalid paths");
  }
  if (Object.keys(spec.paths).length === 0) {
    throw new Error("Invalid spec: paths object cannot be empty");
  }
  if (!Array.isArray(spec.tags) || spec.tags.length === 0) {
    throw new Error(
      "Invalid spec: missing or invalid tags array (required for sidebar generation)",
    );
  }

  for (const [index, tag] of spec.tags.entries()) {
    if (!tag || typeof tag.name !== "string" || tag.name.length === 0) {
      throw new Error(`Invalid spec: tag[${index}] must have a non-empty name`);
    }
  }

  console.log("Basic OpenAPI spec validation passed");
  console.log(`API: ${spec.info.title} v${spec.info.version}`);
  logValidationStats(spec);
  return spec;
}

function logValidationStats(spec) {
  const pathCount = Object.keys(spec.paths || {}).length;
  const tagCount = spec.tags?.length || 0;
  const operationCount = Object.values(spec.paths || {}).reduce(
    (count, pathItem) =>
      count + OPENAPI_METHODS.filter((method) => pathItem[method]).length,
    0,
  );
  const schemaCount = Object.keys(spec.components?.schemas || {}).length;

  console.log(
    `Spec stats: ${pathCount} paths, ${tagCount} tags, ${operationCount} operations, ${schemaCount} schemas`,
  );
}

const OPENAPI_METHODS = [
  "get",
  "put",
  "post",
  "delete",
  "options",
  "head",
  "patch",
  "trace",
];

module.exports = {
  validateOpenAPISpec,
};
