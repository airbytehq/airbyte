#!/usr/bin/env node
/**
 * Strip the massive 'api:' field from generated API MDX files
 * This field contains base64-encoded OpenAPI specs that cause mdx-loader to hang
 * The field is not used by the React components, which get data from imported components
 */

const fs = require('fs');
const path = require('path');

// Directories containing generated API files
// Note: These are relative to the docusaurus directory (not src/scripts)
const docusaurusRoot = path.resolve(__dirname, '../../..');
const apiDirs = [
  path.join(docusaurusRoot, 'docs/developers/api-reference'),
  path.join(docusaurusRoot, 'docs/ai-agents/embedded/api-reference'),
];

let processedFiles = 0;
let strippedCount = 0;
let totalBytesRemoved = 0;

console.log('🧹 Stripping api: fields from generated MDX files...\n');

// Recursively get all .api.mdx files
function getAllApiFiles(absolutePath) {
  if (!fs.existsSync(absolutePath)) {
    return [];
  }

  let files = [];
  const entries = fs.readdirSync(absolutePath, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(absolutePath, entry.name);
    if (entry.isDirectory()) {
      files = files.concat(getAllApiFiles(fullPath));
    } else if (entry.name.endsWith('.api.mdx')) {
      files.push(fullPath);
    }
  }

  return files;
}

apiDirs.forEach((absolutePath) => {
  const files = getAllApiFiles(absolutePath);

  files.forEach((filePath) => {
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      const originalSize = content.length;

      // Match the frontmatter pattern and remove the api: field
      const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);

      if (frontmatterMatch) {
        const frontmatter = frontmatterMatch[1];

        // Check if api field exists
        if (frontmatter.includes('api:')) {
          // Remove the api field (it's a long line or could be multiline)
          const updatedFrontmatter = frontmatter
            .split('\n')
            .filter((line) => !line.startsWith('api:'))
            .join('\n');

          // Replace the frontmatter
          const updatedContent = content.replace(
            /^---\n[\s\S]*?\n---/,
            `---\n${updatedFrontmatter}\n---`
          );

          // Write back
          fs.writeFileSync(filePath, updatedContent, 'utf8');

          const newSize = updatedContent.length;
          const bytesRemoved = originalSize - newSize;
          totalBytesRemoved += bytesRemoved;
          strippedCount++;

          // Only log if significant
          if (bytesRemoved > 10000) {
            const fileName = path.relative(path.resolve(__dirname, '../../docs'), filePath);
            console.log(
              `  ✂️  ${fileName}: removed ${(bytesRemoved / 1024).toFixed(1)} KB`
            );
          }
        }
      }
      processedFiles++;
    } catch (error) {
      console.error(`  ❌ Error processing ${filePath}:`, error.message);
    }
  });
});

console.log(`\n✅ Complete!`);
console.log(`   📊 Processed: ${processedFiles} files`);
console.log(`   ✂️  Stripped: ${strippedCount} files`);
console.log(`   💾 Total removed: ${(totalBytesRemoved / 1024 / 1024).toFixed(2)} MB`);
