#!/usr/bin/env node

/**
 * Script to replace RequestSchema components with CreateSourceRequestSchema
 * Runs after prepare-public-api-spec to process regenerated MDX files
 *
 * This script also extracts request body parameters from the OpenAPI spec
 * and passes them as props to the component for dynamic field rendering.
 */

const fs = require('fs');
const path = require('path');
const { PUBLIC_API_SPEC_CACHE_PATH } = require('./constants');

const PROJECT_ROOT = path.join(__dirname, '../../../..');

// Function to recursively find all .api.mdx files
function findApiMdxFiles(dir) {
  let files = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files = files.concat(findApiMdxFiles(fullPath));
    } else if (entry.name.endsWith('.api.mdx')) {
      files.push(fullPath);
    }
  }

  return files;
}

// Get all .api.mdx files from both API reference directories
const apiReferenceDirs = [
  'docs/developers/api-reference',
  'docs/ai-agents/embedded/api-reference'
];

// Function to check if a file should have CreateSourceRequestSchema
// Only source and destination creation/update endpoints should use it
function shouldHaveCreateSourceSchema(filePath) {
  const fileName = path.basename(filePath);

  // Whitelist of endpoints that have configuration: SourceConfiguration or DestinationConfiguration
  const sourceEndpoints = [
    'create-source',
    'patch-source',
    'put-source',
    'update-source'
  ];

  const destinationEndpoints = [
    'create-destination',
    'patch-destination',
    'put-destination',
    'update-destination'
  ];

  const allEndpoints = [...sourceEndpoints, ...destinationEndpoints];

  return allEndpoints.some(endpoint => fileName.startsWith(endpoint));
}

// Load the OpenAPI spec to extract request body parameters
function loadOpenAPISpec() {
  try {
    const specPath = path.join(PROJECT_ROOT, PUBLIC_API_SPEC_CACHE_PATH);
    if (!fs.existsSync(specPath)) {
      console.warn(`⚠️  OpenAPI spec not found at ${specPath}`);
      return null;
    }
    const spec = JSON.parse(fs.readFileSync(specPath, 'utf-8'));
    return spec;
  } catch (error) {
    console.warn(`⚠️  Failed to load OpenAPI spec:`, error.message);
    return null;
  }
}

// Extract request body parameters for a specific endpoint
function getRequestBodyParams(spec, operationId) {
  if (!spec || !spec.paths) {
    return [];
  }

  // Find the operation in the spec
  for (const pathKey in spec.paths) {
    const pathItem = spec.paths[pathKey];
    for (const method in pathItem) {
      const operation = pathItem[method];
      if (operation.operationId === operationId) {
        // Extract parameters from requestBody
        if (operation.requestBody && operation.requestBody.content) {
          const jsonContent = operation.requestBody.content['application/json'];
          if (jsonContent && jsonContent.schema) {
            const schema = jsonContent.schema;
            // Resolve $ref if needed
            if (schema.$ref) {
              const refPath = schema.$ref.split('/');
              let resolved = spec;
              for (const part of refPath.slice(1)) {
                resolved = resolved[part];
              }
              if (resolved && resolved.properties) {
                return Object.entries(resolved.properties).map(([key, prop]) => ({
                  name: key,
                  type: prop.type || 'string',
                  required: resolved.required && resolved.required.includes(key),
                  description: prop.description || ''
                }));
              }
            } else if (schema.properties) {
              return Object.entries(schema.properties).map(([key, prop]) => ({
                name: key,
                type: prop.type || 'string',
                required: schema.required && schema.required.includes(key),
                description: prop.description || ''
              }));
            }
          }
        }
      }
    }
  }

  return [];
}

let MDX_FILES = [];
for (const dir of apiReferenceDirs) {
  const fullDir = path.join(PROJECT_ROOT, dir);
  if (fs.existsSync(fullDir)) {
    const allFiles = findApiMdxFiles(fullDir);
    // Filter to only source and destination creation/update endpoints
    const filteredFiles = allFiles.filter(shouldHaveCreateSourceSchema);
    // Convert to relative paths from PROJECT_ROOT
    MDX_FILES = MDX_FILES.concat(filteredFiles.map(f => path.relative(PROJECT_ROOT, f)));
  }
}

function replaceRequestSchema(filePath, spec) {
  console.log(`\n📝 Processing: ${filePath}`);

  const fullPath = path.join(PROJECT_ROOT, filePath);

  if (!fs.existsSync(fullPath)) {
    console.warn(`⚠️  File not found: ${fullPath}`);
    return false;
  }

  let content = fs.readFileSync(fullPath, 'utf-8');
  const originalLength = content.length;

  // Extract operationId from frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  let operationId = null;
  if (frontmatterMatch) {
    const frontmatter = frontmatterMatch[1];
    const opIdMatch = frontmatter.match(/operationId:\s*(\w+)/);
    if (opIdMatch) {
      operationId = opIdMatch[1];
    }
  }

  // Get request body parameters if we have the spec and operationId
  let paramsString = '';
  if (spec && operationId) {
    const params = getRequestBodyParams(spec, operationId);
    if (params.length > 0) {
      paramsString = ` requestBodyParams={${JSON.stringify(params)}}`;
    }
  }

  // Replace RequestSchema imports
  const importPattern = /import\s+RequestSchema\s+from\s+["']@theme\/RequestSchema["'];?/g;
  content = content.replace(importPattern, '// CreateSourceRequestSchema is auto-registered in MDXComponents');

  // Replace <RequestSchema ... /> components
  const componentPattern = /<RequestSchema\s+[^>]*\/>/gs;
  content = content.replace(componentPattern, `<CreateSourceRequestSchema${paramsString} />`);

  // Replace <RequestSchema ... > ... </RequestSchema> components
  const multilinePattern = /<RequestSchema\s+[^>]*>[\s\S]*?<\/RequestSchema>/g;
  content = content.replace(multilinePattern, `<CreateSourceRequestSchema${paramsString} />`);

  const newLength = content.length;
  const sizeDiff = originalLength - newLength;

  if (originalLength !== newLength) {
    fs.writeFileSync(fullPath, content, 'utf-8');
    console.log(`✅ Updated: ${filePath}`);
    console.log(`   Size reduction: ${(sizeDiff / 1024).toFixed(2)} KB`);
    if (paramsString) {
      console.log(`   Request params: ${params.length} fields extracted`);
    }
    return true;
  } else {
    console.log(`ℹ️  No changes needed: ${filePath}`);
    return false;
  }
}

function main() {
  console.log('🔄 Replacing RequestSchema components...\n');
  console.log(`   Scanning ${apiReferenceDirs.length} API reference directories...`);

  // Load the OpenAPI spec for parameter extraction
  const spec = loadOpenAPISpec();
  if (spec) {
    console.log('✅ OpenAPI spec loaded successfully');
  } else {
    console.log('⚠️  OpenAPI spec not available - request body params will not be extracted');
  }

  // Count total files before filtering
  let totalFiles = 0;
  for (const dir of apiReferenceDirs) {
    const fullDir = path.join(PROJECT_ROOT, dir);
    if (fs.existsSync(fullDir)) {
      totalFiles += findApiMdxFiles(fullDir).length;
    }
  }

  console.log(`   Found ${totalFiles} .api.mdx files total`);
  console.log(`   Filtered to ${MDX_FILES.length} files with SourceConfiguration\n`);

  let filesUpdated = 0;
  let filesProcessed = 0;
  let totalSizeReduction = 0;

  for (const mdxFile of MDX_FILES) {
    filesProcessed++;
    const fullPath = path.join(PROJECT_ROOT, mdxFile);
    if (fs.existsSync(fullPath)) {
      const originalLength = fs.readFileSync(fullPath, 'utf-8').length;
      if (replaceRequestSchema(mdxFile, spec)) {
        const newLength = fs.readFileSync(fullPath, 'utf-8').length;
        const reduction = originalLength - newLength;
        totalSizeReduction += reduction;
        filesUpdated++;
      }
    }
  }

  console.log(`\n✨ Complete!`);
  console.log(`   📊 Processed: ${filesProcessed} files`);
  console.log(`   ✂️  Updated: ${filesUpdated} files`);
  if (totalSizeReduction > 0) {
    console.log(`   💾 Total size reduction: ${(totalSizeReduction / 1024 / 1024).toFixed(2)} MB`);
    console.log('\n📋 Summary:');
    console.log('   - RequestSchema imports replaced with comments');
    console.log('   - RequestSchema components replaced with CreateSourceRequestSchema');
    console.log('   - Request body parameters dynamically extracted from OpenAPI spec');
    console.log('   - MDX files are now much smaller');
  }
}

main();
