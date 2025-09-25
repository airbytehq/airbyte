
function yamlLoaderPlugin(context, options) {
  return {
    name: "yaml-loader-plugin",
    configureWebpack() {
      return {
        module: {
          rules: [
            {
              test: /\.ya?ml$/,
              use: "yaml-loader",
            },
            {
              test: /\.html$/i,
              loader: "html-loader",
            },
          ],
        },
      };
    },
  };
}

module.exports = yamlLoaderPlugin;
