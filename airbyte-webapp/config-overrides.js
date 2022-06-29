// eslint-disable-next-line @typescript-eslint/no-var-requires
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  webpack: (webpackConfig) => {
    const instanceOfMiniCssExtractPlugin = webpackConfig.plugins.find(
      (plugin) => plugin instanceof MiniCssExtractPlugin
    );
    instanceOfMiniCssExtractPlugin.options.ignoreOrder = true;

    return webpackConfig;
  },
};
