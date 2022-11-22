/* eslint-disable @typescript-eslint/no-var-requires */
const { merge } = require("lodash");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const webpack = require("webpack");

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      const overriddenConfig = merge({}, webpackConfig, {
        // suppress warnings of libraries missing source maps
        ignoreWarnings: [/Failed to parse source map/],
        // add required polyfills for some libraries
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
        // polyfill global nodeJS variables required by some libraries
        new webpack.ProvidePlugin({
          process: "process/browser",
          Buffer: ["buffer", "Buffer"],
        }),
      ];

      // required for process/browser polyfill to work
      // https://github.com/microsoft/PowerBI-visuals-tools/issues/365#issuecomment-1099716186
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
