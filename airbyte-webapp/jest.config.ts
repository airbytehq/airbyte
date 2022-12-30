/* eslint-disable jest/no-jest-import */
import type { Config } from "jest";

const jestConfig = async (): Promise<Config> => {
  return {
    verbose: true,
    transformIgnorePatterns: [],
    snapshotSerializers: ["./scripts/classname-serializer.js"],
    coveragePathIgnorePatterns: [".stories.tsx"],
    modulePathIgnorePatterns: ["src/.*/__mocks__", "src/.*/package.json"],
    testEnvironment: "jsdom",
    moduleDirectories: ["node_modules", "src/test-utils", "src"],
    moduleNameMapper: {
      "\\.(scss)$": "identity-obj-proxy",
      "\\.(css|png|svg)$": "test-utils/mockModule.js",
    },
    setupFilesAfterEnv: ["./src/setupTests.ts"],
  };
};

export default jestConfig;
