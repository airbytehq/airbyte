/* eslint-disable @typescript-eslint/no-var-requires */
const { merge } = require("lodash");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const webpack = require("webpack");

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      const overriddenConfig = merge({}, webpackConfig, {
        ignoreWarnings: [/Failed to parse source map/],
        resolve: {
          fallback: {
            https: false,
            http: false,
          },
          alias: {
            process: "process/browser",
          },
        },
        module: {
          rules: [],
        },
      });

      overriddenConfig.plugins = [
        ...webpackConfig.plugins.filter((element) => {
          return !(element instanceof MiniCssExtractPlugin);
        }),
        new MiniCssExtractPlugin({
          ignoreOrder: true,
          filename: "static/css/[name].[contenthash:8].css",
          chunkFilename: "static/css/[name].[contenthash:8].chunk.css",
        }),
        new webpack.ProvidePlugin({
          process: "process/browser",
          Buffer: ["buffer", "Buffer"],
        }),
      ];

      overriddenConfig.module.rules.push({
        test: /\.m?js/,
        resolve: {
          fullySpecified: false,
        },
      });
      return overriddenConfig;
    },
  },
};
