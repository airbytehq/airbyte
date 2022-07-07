// eslint-disable-next-line @typescript-eslint/no-var-requires
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      webpackConfig = {
        ...webpackConfig,
        plugins: [
          ...webpackConfig.plugins.filter((element) => {
            if (element.options) {
              return !element.options.hasOwnProperty("ignoreOrder");
            }
            return true;
          }),
          new MiniCssExtractPlugin({
            ignoreOrder: true,
          }),
        ],
      };
      return webpackConfig;
    },
  },
};
