/**
 * Webpack plugin to debug which files are being processed by mdx-loader
 * This helps identify files that may be causing the build to hang
 */

module.exports = function mdxDebugPlugin() {
  let processedCount = 0;
  let lastLogTime = Date.now();

  return {
    name: "mdx-debug-plugin",
    configureWebpack(config, isServer) {
      // Intercept the mdx-loader rule
      const webpackConfig = {
        module: {
          rules: [
            {
              test: /\.mdx?$/,
              use: [
                {
                  loader: "mdx-debug-loader",
                  options: {
                    onLoad(filePath) {
                      processedCount++;
                      const now = Date.now();
                      const timeSinceLastLog = now - lastLogTime;

                      // Log every file or at least every 2 seconds
                      if (processedCount % 5 === 0 || timeSinceLastLog > 2000) {
                        console.log(
                          `📄 [MDX Debug] Processing file #${processedCount}: ${filePath}`
                        );
                        lastLogTime = now;
                      }
                    },
                  },
                },
              ],
            },
          ],
        },
      };

      return webpackConfig;
    },
  };
};
