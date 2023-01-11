module.exports = {
  env: {
    test: {
      // Define presets used to compile code when running jest tests
      presets: [
        ["@babel/preset-env", { targets: { node: "current" } }],
        ["@babel/preset-react", { runtime: "automatic" }],
        "@babel/preset-typescript",
      ],
    },
  },
};
