import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: "../airbyte-api/src/main/openapi/config.yaml",
    output: {
      target: "./src/core/request/GeneratedApi.ts",
      override: {
        operationName: (operation) =>
          `use${operation.operationId
            .split("")
            .map((v, i) => (i === 0 ? v.toUpperCase() : v))
            .join("")}`,
        mutator: {
          path: "./src/core/request/useApiOverride.ts",
          name: "useApiOverride",
        },
      },
    },
  },
});
