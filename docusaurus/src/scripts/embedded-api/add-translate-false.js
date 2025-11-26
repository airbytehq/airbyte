/**
 * Post-processing script to add translate: false to generated OpenAPI MDX files.
 * 
 * This script runs after docusaurus gen-api-docs and adds translate: false
 * to the frontmatter of each generated MDX file. This prevents Docusaurus
 * from checking for duplicate translation keys, which would otherwise fail
 * because the OpenAPI spec has multiple endpoints with the same operation names.
 */

const fs = require("fs");
const path = require("path");
const { API_DOCS_OUTPUT_DIR, PROJECT_ROOT } = require("./constants");

const API_DOCS_PATH = path.resolve(PROJECT_ROOT, API_DOCS_OUTPUT_DIR);

function addTranslateFalseToFile(filePath) {
  const content = fs.readFileSync(filePath, "utf8");
  
  // Check if file has frontmatter
  if (!content.startsWith("---")) {
    console.warn(`Skipping ${filePath}: no frontmatter found`);
    return false;
  }
  
  // Check if translate: false is already present
  if (content.includes("translate: false")) {
    return false;
  }
  
  // Find the end of frontmatter
  const endOfFrontmatter = content.indexOf("---", 3);
  if (endOfFrontmatter === -1) {
    console.warn(`Skipping ${filePath}: malformed frontmatter`);
    return false;
  }
  
  // Insert translate: false before the closing ---
  const frontmatter = content.substring(0, endOfFrontmatter);
  const rest = content.substring(endOfFrontmatter);
  const newContent = frontmatter + "translate: false\n" + rest;
  
  fs.writeFileSync(filePath, newContent, "utf8");
  return true;
}

function processDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) {
    console.log(`Directory does not exist: ${dirPath}`);
    return;
  }
  
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  let modifiedCount = 0;
  
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    
    if (entry.isDirectory()) {
      modifiedCount += processDirectory(fullPath);
    } else if (entry.name.endsWith(".mdx") || entry.name.endsWith(".md")) {
      if (addTranslateFalseToFile(fullPath)) {
        modifiedCount++;
      }
    }
  }
  
  return modifiedCount;
}

function main() {
  console.log(`Processing MDX files in: ${API_DOCS_PATH}`);
  const modifiedCount = processDirectory(API_DOCS_PATH);
  console.log(`Added translate: false to ${modifiedCount} files`);
}

main();
