import type { Plugin } from "vite";

import fs from "fs";
import path from "path";

import { v4 as uuidV4 } from "uuid";

const buildHash = uuidV4();

export function buildInfo(): Plugin {
  return {
    name: "airbyte/build-info",
    buildStart() {
      fs.writeFileSync(path.resolve(__dirname, "../../public/buildInfo.json"), JSON.stringify({ build: buildHash }));
    },
    config: () => ({
      define: {
        "process.env.BUILD_HASH": JSON.stringify(buildHash),
      },
    }),
  };
}
