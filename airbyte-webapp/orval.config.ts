import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: "../airbyte-api/src/main/openapi/config.yaml",
    output: {
      target: "./src/core/request/GeneratedApi.ts",
      override: {
        mutator: {
          path: "./src/core/request/apiOverride.ts",
          name: "apiOverride",
        },
      },
    },
  },
});
