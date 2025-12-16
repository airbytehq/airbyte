/**
 * Debug wrapper for mdx-loader
 * Logs each file being processed to help identify hanging files
 */

module.exports = async function mdxDebugLoader(source) {
  const filePath = this.resourcePath;
  const now = new Date().toLocaleTimeString();

  // Log the file being processed
  console.log(`[${now}] 🔄 [MDX] Processing: ${filePath}`);

  // Pass through to the next loader in the chain
  // The actual mdx-loader will be called after this
  return source;
};

// Mark as raw to pass through the source as-is
mdxDebugLoader.raw = false;
