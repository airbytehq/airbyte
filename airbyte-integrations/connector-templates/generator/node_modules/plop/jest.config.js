import { resolve } from "node:path";

export default {
  coverageThreshold: {
    global: {
      branches: 40,
      functions: 50,
      lines: 50,
      statements: 50,
    },
  },
  projects: [resolve("./tests/config/jest.config.js")],
  transform: {},
};
