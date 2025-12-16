#!/usr/bin/env node

/**
 * Temporarily remove StatusCodes components from API MDX files
 * This is a temporary fix until we create a proper custom component
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

function removeStatusCodes(filePath) {
  const fullPath = path.join(PROJECT_ROOT, filePath);

  if (!fs.existsSync(fullPath)) {
    return false;
  }

  let content = fs.readFileSync(fullPath, 'utf-8');
  const originalLength = content.length;

  // Remove the StatusCodes import
  content = content.replace(/import\s+StatusCodes\s+from\s+["']@theme\/StatusCodes["'];?\n?/g, '');

  // Remove StatusCodes components - they span from <StatusCodes to </StatusCodes>
  // Use a state machine to handle nested braces
  let result = '';
  let i = 0;

  while (i < content.length) {
    const remaining = content.substring(i);
    const startIdx = remaining.indexOf('<StatusCodes');

    if (startIdx === -1) {
      result += remaining;
      break;
    }

    // Add everything before the StatusCodes component
    result += remaining.substring(0, startIdx);

    // Find the closing </StatusCodes>
    const componentStart = i + startIdx;
    const closeIdx = content.indexOf('</StatusCodes>', componentStart);

    if (closeIdx === -1) {
      result += remaining.substring(startIdx);
      break;
    }

    // Skip past the closing tag
    i = closeIdx + '</StatusCodes>'.length;

    // Skip any trailing whitespace/newlines
    while (i < content.length && /[\n\r\s]/.test(content[i])) {
      i++;
    }
  }

  content = result;

  const newLength = content.length;
  const sizeDiff = originalLength - newLength;

  if (sizeDiff > 0) {
    fs.writeFileSync(fullPath, content, 'utf-8');
    return { reduced: true, bytes: sizeDiff };
  }

  return false;
}

function main() {
  console.log('🗑️  Removing StatusCodes components...\n');
  console.log(`   Scanning ${apiReferenceDirs.length} API reference directories...`);
  console.log(`   Found ${MDX_FILES.length} .api.mdx files\n`);

  let filesUpdated = 0;
  let filesProcessed = 0;
  let totalSizeReduction = 0;

  for (const mdxFile of MDX_FILES) {
    filesProcessed++;
    const result = removeStatusCodes(mdxFile);

    if (result && result.reduced) {
      filesUpdated++;
      totalSizeReduction += result.bytes;

      if (result.bytes > 1000) {
        console.log(`   🗑️  ${path.basename(mdxFile)}: removed ${(result.bytes / 1024).toFixed(1)} KB`);
      }
    }
  }

  console.log(`\n✨ Complete!`);
  console.log(`   📊 Processed: ${filesProcessed} files`);
  console.log(`   🗑️  Updated: ${filesUpdated} files`);
  if (totalSizeReduction > 0) {
    console.log(`   💾 Total size reduction: ${(totalSizeReduction / 1024 / 1024).toFixed(2)} MB`);
  }
}

main();
