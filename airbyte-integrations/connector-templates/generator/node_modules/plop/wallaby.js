module.exports = function (wallaby) {
  return {
    files: ["bin/**/*.js", "src/**/*.js", "!tests/**/*.spec.js"],
    tests: ["tests/**/*.spec.js"],
    env: {
      type: "node",
      runner: "node",
    },
    testFramework: "jest",
    debug: true,
  };
};
