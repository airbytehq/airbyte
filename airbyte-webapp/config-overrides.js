const { addWebpackAlias } = require("customize-cra");
const rewireReactHotLoader = require("react-app-rewire-hot-loader");

module.exports = function override(config, env) {
  config = rewireReactHotLoader(config, env);
  config = addWebpackAlias({
    "react-dom": "@hot-loader/react-dom"
  })(config, env);
  return config;
};
