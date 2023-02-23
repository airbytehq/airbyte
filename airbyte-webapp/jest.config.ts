// eslint-disable-next-line jest/no-jest-import
import type { Config } from "jest";

const jestConfig: Config = {
  verbose: true,
  // Required to overwrite the default which would ignore node_modules from transformation,
  // but several node_modules are not transpiled so they would fail without babel transformation running
  transformIgnorePatterns: [],
  snapshotSerializers: ["./src/test-utils/classname-serializer.js"],
  coveragePathIgnorePatterns: ["\\.stories\\.tsx$"],
  modulePathIgnorePatterns: ["src/.*/__mocks__"],
  testEnvironment: "jsdom",
  moduleDirectories: ["node_modules", "src"],
  moduleNameMapper: {
    "\\.module\\.scss$": "test-utils/mock-data/mockIdentity.js",
    "\\.(css|png|svg|scss)$": "test-utils/mock-data/mockEmpty.js",
  },
  setupFilesAfterEnv: ["./src/test-utils/setup-tests.ts"],
};

export default jestConfig;
