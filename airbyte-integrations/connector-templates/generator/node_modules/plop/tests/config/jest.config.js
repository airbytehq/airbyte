import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

export default {
  rootDir: join(__dirname, "../.."),
  displayName: "node",
  testEnvironment: "jest-environment-node",
  testMatch: ["**/tests/**.spec.js"],
  snapshotSerializers: ["jest-snapshot-serializer-ansi"],
  transform: {},
  setupFilesAfterEnv: [join(__dirname, "./jest.setup.js")],
};
