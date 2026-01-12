#!/usr/bin/env node

/**
 * Strip massive response schemas from StatusCodes components
 * The responses prop contains the entire SourceConfiguration schema for each status code
 * but is never actually rendered. We replace it with status codes + descriptions only.
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

let MDX_FILES = [];
for (const dir of apiReferenceDirs) {
  const fullDir = path.join(PROJECT_ROOT, dir);
  if (fs.existsSync(fullDir)) {
    const files = findApiMdxFiles(fullDir);
    MDX_FILES = MDX_FILES.concat(files.map(f => path.relative(PROJECT_ROOT, f)));
  }
}

function extractStatusCodeDescriptions(responsesStr) {
  // Parse the responses object to extract just status codes and descriptions
  // Example: "200":{"description":"Success"...} -> "200":{"description":"Success"}

  const statusMap = {};

  // Match patterns like "200": { ... "description": "text" ... }
  // Need to handle escaped quotes in descriptions
  const statusPattern = /"(\d{3})":\s*\{[^}]*"description"\s*:\s*"((?:\\.|[^"\\])*)"[^}]*\}/g;
  let match;

  while ((match = statusPattern.exec(responsesStr)) !== null) {
    statusMap[match[1]] = match[2];
  }

  if (Object.keys(statusMap).length === 0) {
    return null; // Couldn't parse, keep original
  }

  // Build simplified responses object with proper JSON escaping
  const simplified = {};
  for (const [code, desc] of Object.entries(statusMap)) {
    // Ensure description is properly escaped for JSON
    simplified[code] = { description: desc };
  }

  try {
    return JSON.stringify(simplified);
  } catch (e) {
    return null; // If stringification fails, keep original
  }
}

function stripResponseSchemas(filePath) {
  const fullPath = path.join(PROJECT_ROOT, filePath);

  if (!fs.existsSync(fullPath)) {
    return false;
  }

  let content = fs.readFileSync(fullPath, 'utf-8');
  const originalLength = content.length;

  // Find all responses={...} patterns and replace them with simplified versions
  // We need to find where responses={ starts and count braces to find the closing }

  let totalReduction = 0;
  let searchStart = 0;

  while (true) {
    const responsesStart = content.indexOf('responses=', searchStart);
    if (responsesStart === -1) {
      break;
    }

    // Check if this is responses={ (the prop value)
    if (responsesStart + 10 >= content.length || content[responsesStart + 10] !== '{') {
      searchStart = responsesStart + 10;
      continue;
    }

    // Find the closing } by counting braces
    let braceCount = 1; // Start with 1 for the opening {
    let pos = responsesStart + 11; // After "responses={"

    while (pos < content.length && braceCount > 0) {
      if (content[pos] === '{') {
        braceCount++;
      } else if (content[pos] === '}') {
        braceCount--;
      }
      pos++;
    }

    if (braceCount === 0) {
      const responsesEnd = pos;
      const responsesStr = content.substring(responsesStart + 10, responsesEnd);

      // Only simplify if the responses object is very large (contains schemas)
      if (responsesStr.length > 1000) {
        const simplified = extractStatusCodeDescriptions(responsesStr);

        if (simplified && simplified.length < responsesStr.length) {
          const before = content.substring(0, responsesStart);
          const after = content.substring(responsesEnd);
          content = before + 'responses=' + simplified + after;

          totalReduction += responsesStr.length - simplified.length;
          searchStart = responsesStart + ('responses='.length + simplified.length);
        } else {
          // If simplification fails, just use empty object to be safe
          const before = content.substring(0, responsesStart);
          const after = content.substring(responsesEnd);
          content = before + 'responses={{}}' + after;

          totalReduction += responsesStr.length - 2; // {{}} is 2 chars
          searchStart = responsesStart + ('responses={{}}'.length);
        }
      } else {
        searchStart = responsesEnd;
      }
    } else {
      break;
    }
  }

  const newLength = content.length;
  const sizeDiff = originalLength - newLength;

  if (sizeDiff > 0) {
    fs.writeFileSync(fullPath, content, 'utf-8');
    return { reduced: true, bytes: sizeDiff };
  }

  return false;
}

function main() {
  console.log('🧹 Stripping response schemas from StatusCodes...\n');
  console.log(`   Scanning ${apiReferenceDirs.length} API reference directories...`);
  console.log(`   Found ${MDX_FILES.length} .api.mdx files\n`);

  let filesUpdated = 0;
  let filesProcessed = 0;
  let totalSizeReduction = 0;

  for (const mdxFile of MDX_FILES) {
    filesProcessed++;
    const result = stripResponseSchemas(mdxFile);

    if (result && result.reduced) {
      filesUpdated++;
      totalSizeReduction += result.bytes;

      if (result.bytes > 10000) {
        console.log(`   ✂️  ${path.basename(mdxFile)}: removed ${(result.bytes / 1024).toFixed(1)} KB`);
      }
    }
  }

  console.log(`\n✨ Complete!`);
  console.log(`   📊 Processed: ${filesProcessed} files`);
  console.log(`   ✂️  Updated: ${filesUpdated} files`);
  if (totalSizeReduction > 0) {
    console.log(`   💾 Total size reduction: ${(totalSizeReduction / 1024 / 1024).toFixed(2)} MB`);
  }
}

main();
