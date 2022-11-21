// eslint-disable-next-line @typescript-eslint/no-var-requires
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  jest: {
    configure: (jestConfig) => {
      return {
        ...jestConfig,
        setupFiles: [...jestConfig.setupFiles, "./__test__/globalSetup.ts"],
      };
    },
  },
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
            filename: "static/css/[name].[contenthash:8].css",
            chunkFilename: "static/css/[name].[contenthash:8].chunk.css",
          }),
        ],
      };
      return webpackConfig;
    },
  },
};
