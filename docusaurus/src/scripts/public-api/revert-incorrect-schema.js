#!/usr/bin/env node

/**
 * Script to revert CreateSourceRequestSchema components from endpoints that shouldn't have them
 * Only source and destination creation/update endpoints should have this component
 */

const fs = require('fs');
const path = require('path');

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
function shouldHaveCreateSourceSchema(fileName) {
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

function removeIncorrectSchema(filePath) {
  const fullPath = path.join(PROJECT_ROOT, filePath);

  if (!fs.existsSync(fullPath)) {
    return false;
  }

  let content = fs.readFileSync(fullPath, 'utf-8');
  const originalLength = content.length;

  // Remove the CreateSourceRequestSchema import comment if present
  content = content.replace(/\/\/ CreateSourceRequestSchema is auto-registered in MDXComponents\n/g, '');

  // Remove <CreateSourceRequestSchema /> components
  const componentPattern = /<CreateSourceRequestSchema\s*\/>/g;
  content = content.replace(componentPattern, '');

  const newLength = content.length;
  const sizeDiff = originalLength - newLength;

  if (sizeDiff > 0) {
    fs.writeFileSync(fullPath, content, 'utf-8');
    return { removed: true, bytes: sizeDiff };
  }

  return false;
}

function main() {
  console.log('🔄 Reverting CreateSourceRequestSchema from incorrect endpoints...\n');
  console.log(`   Scanning ${apiReferenceDirs.length} API reference directories...`);

  let filesWithSchema = 0;
  let filesReverted = 0;
  let totalSizeReduction = 0;

  for (const dir of apiReferenceDirs) {
    const fullDir = path.join(PROJECT_ROOT, dir);
    if (fs.existsSync(fullDir)) {
      const allFiles = findApiMdxFiles(fullDir);

      for (const filePath of allFiles) {
        const relativePath = path.relative(PROJECT_ROOT, filePath);
        const fileName = path.basename(filePath);

        try {
          const content = fs.readFileSync(filePath, 'utf-8');
          if (content.includes('<CreateSourceRequestSchema')) {
            filesWithSchema++;

            // If this file shouldn't have it, remove it
            if (!shouldHaveCreateSourceSchema(fileName)) {
              const result = removeIncorrectSchema(relativePath);
              if (result && result.removed) {
                filesReverted++;
                totalSizeReduction += result.bytes;
                console.log(`   ✂️  Reverted: ${fileName}`);
              }
            }
          }
        } catch (error) {
          console.error(`   ❌ Error processing ${relativePath}:`, error.message);
        }
      }
    }
  }

  console.log(`\n✨ Complete!`);
  console.log(`   📊 Files with CreateSourceRequestSchema: ${filesWithSchema}`);
  console.log(`   ✂️  Reverted: ${filesReverted} files`);
  if (totalSizeReduction > 0) {
    console.log(`   💾 Total size reduction: ${(totalSizeReduction / 1024 / 1024).toFixed(2)} MB`);
  }
}

main();
