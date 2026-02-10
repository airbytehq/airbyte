/**
 * OpenAPI specification validator using @seriousme/openapi-schema-validator
 * 
 * This validator uses a purpose-built OpenAPI validation library that supports
 * OpenAPI 2.0, 3.0.x, and 3.1.x specifications. It's been tested on over 2,000 
 * real-world APIs from AWS, Microsoft, Google, etc.
 * 
 * Ensures compatibility with:
 * 1. The docusaurus-plugin-openapi-docs generator
 * 2. Our custom sidebar filtering logic in docusaurus.config.js
 * 3. The Docusaurus theme-openapi-docs components
 */

// Note: Using dynamic import since this package is ESM-only
// We'll import it inside the async function to maintain CommonJS compatibility

/**
 * Validates an OpenAPI specification using the schema validator
 * @param {Object} spec - The OpenAPI spec to validate
 * @throws {Error} If validation fails
 * @returns {Object} The validated spec with additional metadata
 */
async function validateOpenAPISpec(spec) {
  console.log("🔍 Validating OpenAPI spec with @seriousme/openapi-schema-validator...");
  
  try {
    // Dynamic import to handle ESM module in CommonJS context
    const { Validator } = await import("@seriousme/openapi-schema-validator");
    
    // Create validator instance
    const validator = new Validator();
    
    // Validate the spec
    const result = await validator.validate(spec);
    
    if (!result.valid) {
      let errorMessages = "Unknown validation errors";
      
      if (result.errors && Array.isArray(result.errors)) {
        errorMessages = result.errors.map(err => {
          const path = err.instancePath || err.schemaPath || 'unknown';
          const message = err.message || 'validation failed';
          return `  • ${path}: ${message}`;
        }).join('\n');
      } else if (result.errors) {
        // Handle case where errors is not an array
        errorMessages = `  • ${String(result.errors)}`;
      }
      
      throw new Error(`OpenAPI spec validation failed:\n${errorMessages}`);
    }

    // Get the validated specification
    const validatedSpec = validator.specification;
    const version = validator.version;
    
    console.log(`✅ OpenAPI spec validation passed!`);
    
    // Perform additional custom validations for our specific use case
    try {
      performDocumentationSpecificValidations(validatedSpec);
    } catch (validationError) {
      // Convert validation warnings to non-fatal warnings for undefined tags
      if (validationError.message && validationError.message.includes('undefined tags')) {
        console.warn(`⚠️  ${validationError.message}`);
        console.warn(`📝 This may cause missing sidebar sections in the documentation`);
      } else {
        // Re-throw other validation errors
        throw validationError;
      }
    }
    
    // Log validation success with stats
    const stats = generateValidationStats(validatedSpec);
    console.log(`📊 Spec stats: ${stats.pathCount} paths, ${stats.tagCount} tags, ${stats.operationCount} operations`);
    
    return validatedSpec;
    
  } catch (importError) {
    // Fallback to basic validation if the import fails
    console.warn("⚠️  Could not load OpenAPI schema validator, using basic validation:", importError.message);
    return performBasicValidation(spec);
  }
}

/**
 * Performs additional validations specific to our documentation needs
 * @param {Object} spec - The validated OpenAPI spec
 */
function performDocumentationSpecificValidations(spec) {
  // 1. Ensure tags are defined (critical for sidebar generation)
  if (!spec.tags || !Array.isArray(spec.tags) || spec.tags.length === 0) {
    throw new Error("OpenAPI spec must have tags array (required for sidebar generation)");
  }

  // 2. Validate that every defined tag has at least one operation (critical for docs)
  const definedTags = new Set(spec.tags.map(tag => tag.name));
  const usedTags = new Set();

  for (const [path, pathItem] of Object.entries(spec.paths)) {
    const httpMethods = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'];
    
    for (const method of httpMethods) {
      const operation = pathItem[method];
      if (operation?.tags) {
        operation.tags.forEach(tag => {
          usedTags.add(tag);
        });
      }
    }
  }

  // 3. Critical: Every defined tag must have at least one operation
  const unusedTags = Array.from(definedTags).filter(tag => !usedTags.has(tag));
  if (unusedTags.length > 0) {
    throw new Error(`Defined tags have no operations and will not appear in docs: ${unusedTags.join(', ')}`);
  }

  // 4. Warn about operations using undefined tags (but don't fail - let them be uncategorized)
  const undefinedTags = Array.from(usedTags).filter(tag => !definedTags.has(tag));
  if (undefinedTags.length > 0) {
    console.warn(`⚠️  Operations reference undefined tags (will be uncategorized): ${undefinedTags.join(', ')}`);
  }

  // 4. Validate that operations have required fields for documentation
  const criticalIssues = [];
  let operationsWithIssues = 0;
  
  for (const [path, pathItem] of Object.entries(spec.paths)) {
    const httpMethods = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'];
    
    for (const method of httpMethods) {
      const operation = pathItem[method];
      if (operation) {
        const operationRef = `${path}[${method.toUpperCase()}]`;
        
        // Critical: operationId is required for MDX generation
        if (!operation.operationId) {
          criticalIssues.push(`${operationRef} missing operationId (required for MDX file generation)`);
        }
        
        // Critical: tags are required for sidebar organization
        if (!operation.tags || operation.tags.length === 0) {
          criticalIssues.push(`${operationRef} missing tags (required for sidebar grouping)`);
        }
        
        // Critical: responses are required
        if (!operation.responses || Object.keys(operation.responses).length === 0) {
          criticalIssues.push(`${operationRef} missing responses (required for documentation)`);
        }
        
        // Warning: summary is recommended
        if (!operation.summary) {
          console.warn(`⚠️  ${operationRef} missing summary (recommended for UI display)`);
          operationsWithIssues++;
        }

        // Warning: should have at least one success response
        if (operation.responses) {
          const responseCodes = Object.keys(operation.responses);
          const hasSuccessResponse = responseCodes.some(code => 
            code.startsWith('2') || code === 'default'
          );
          
          if (!hasSuccessResponse) {
            console.warn(`⚠️  ${operationRef} has no success response (2xx or default)`);
          }
        }
      }
    }
  }
  
  // Throw error if there are critical issues
  if (criticalIssues.length > 0) {
    throw new Error(`Critical OpenAPI documentation issues found:\n${criticalIssues.map(issue => `  • ${issue}`).join('\n')}`);
  }

  if (operationsWithIssues > 0) {
    console.warn(`⚠️  Found ${operationsWithIssues} operation(s) with potential documentation issues`);
  }

  console.log(`✅ Documentation-specific validations passed`);
  console.log(`🏷️  Tags: ${definedTags.size} defined, all have operations (will appear in docs)`);
  if (undefinedTags.length > 0) {
    console.log(`🏷️  Additional tags: ${undefinedTags.length} used by operations but not formally defined`);
  }
}

/**
 * Fallback basic validation if the schema validator can't be loaded
 * @param {Object} spec - The OpenAPI spec
 * @returns {Object} The spec with basic validation
 */
function performBasicValidation(spec) {
  console.log("🔍 Performing basic OpenAPI spec validation...");
  
  // Basic structure validation
  if (!spec || typeof spec !== "object") {
    throw new Error("Invalid spec: not an object");
  }

  if (!spec.openapi && !spec.swagger) {
    throw new Error("Invalid spec: missing openapi or swagger version field");
  }

  if (!spec.info || !spec.info.title) {
    throw new Error("Invalid spec: missing info.title");
  }

  if (!spec.info.version) {
    throw new Error("Invalid spec: missing info.version");
  }
  
  // Check for empty title
  if (spec.info.title === "") {
    throw new Error("Invalid spec: info.title cannot be empty");
  }

  if (!spec.paths || typeof spec.paths !== "object") {
    throw new Error("Invalid spec: missing or invalid paths");
  }
  
  // Check for empty paths
  if (Object.keys(spec.paths).length === 0) {
    throw new Error("Invalid spec: paths object cannot be empty");
  }

  if (!spec.tags || !Array.isArray(spec.tags)) {
    throw new Error("Invalid spec: missing or invalid tags array (required for sidebar generation)");
  }
  
  // Check for empty tags
  if (spec.tags.length === 0) {
    throw new Error("Invalid spec: tags array cannot be empty (required for sidebar generation)");
  }
  
  // Check tag structure
  for (let i = 0; i < spec.tags.length; i++) {
    const tag = spec.tags[i];
    if (!tag || typeof tag !== "object") {
      throw new Error(`Invalid spec: tag[${i}] must be an object`);
    }
    if (!tag.name || typeof tag.name !== "string" || tag.name === "") {
      throw new Error(`Invalid spec: tag[${i}] must have a non-empty name`);
    }
  }

  console.log(`✅ Basic OpenAPI spec validation passed`);
  console.log(`📋 API: ${spec.info.title} v${spec.info.version}`);
  
  const stats = generateValidationStats(spec);
  console.log(`📊 Spec stats: ${stats.pathCount} paths, ${stats.tagCount} tags, ${stats.operationCount} operations`);
  
  return spec;
}

/**
 * Generates validation statistics for logging
 * @param {Object} spec - The OpenAPI spec
 * @returns {Object} Statistics object
 */
function generateValidationStats(spec) {
  const pathCount = Object.keys(spec.paths || {}).length;
  const tagCount = spec.tags?.length || 0;
  
  let operationCount = 0;
  for (const pathItem of Object.values(spec.paths || {})) {
    const methods = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'];
    operationCount += methods.filter(method => pathItem[method]).length;
  }

  const schemaCount = spec.components?.schemas ? Object.keys(spec.components.schemas).length : 0;

  return {
    pathCount,
    tagCount,
    operationCount,
    schemaCount,
    version: spec.info?.version || 'unknown',
    title: spec.info?.title || 'Unknown API'
  };
}

module.exports = {
  validateOpenAPISpec,
};
