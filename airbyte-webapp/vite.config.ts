import fs from "fs";
import path from "path";

import basicSsl from "@vitejs/plugin-basic-ssl";
import react from "@vitejs/plugin-react";
import { loadEnv, Plugin, UserConfig } from "vite";
import { defineConfig } from "vite";
import checker from "vite-plugin-checker";
import svgrPlugin from "vite-plugin-svgr";
import viteTsconfigPaths from "vite-tsconfig-paths";

// https://github.com/bvaughn/react-virtualized/issues/1632
const WRONG_CODE = `import { bpfrpt_proptype_WindowScroller } from "../WindowScroller.js";`;
export function patchReactVirtualized(): Plugin {
  return {
    name: "flat:react-virtualized",
    // Note: we cannot use the `transform` hook here
    //       because libraries are pre-bundled in vite directly,
    //       plugins aren't able to hack that step currently.
    //       so instead we manually edit the file in node_modules.
    //       all we need is to find the timing before pre-bundling.
    configResolved() {
      const file = require
        .resolve("react-lazylog/node_modules/react-virtualized")
        .replace(
          path.join("dist", "commonjs", "index.js"),
          path.join("dist", "es", "WindowScroller", "utils", "onScroll.js")
        );
      const code = fs.readFileSync(file, "utf-8");
      const modified = code.replace(WRONG_CODE, "");
      fs.writeFileSync(file, modified);
    },
  };
}

export default defineConfig(({ mode }) => {
  // Load variables from all .env files
  process.env = {
    ...process.env,
    ...loadEnv(mode, __dirname, ""),
  };

  const config: UserConfig = {
    plugins: [
      basicSsl(),
      react(),
      viteTsconfigPaths(),
      svgrPlugin(),
      checker({
        // Enable checks while building the app (not just in dev mode)
        enableBuild: true,
        overlay: {
          initialIsOpen: false,
          position: "br",
          // Align error popover button with the react-query dev tool button
          badgeStyle: "transform: translate(-60px,-11px)",
        },
        eslint: { lintCommand: `eslint --ext js,ts,tsx src` },
        stylelint: {
          lintCommand: 'stylelint "src/**/*.{css,scss}"',
          // We need to overwrite this during development, since otherwise `files` are wrongly
          // still containing the quotes around them, which they shouldn't
          dev: { overrideConfig: { files: "src/**/*.{css,scss}" } },
        },
        typescript: true,
      }),
      patchReactVirtualized(),
    ],
    // Use `REACT_APP_` as a prefix for environment variables that should be accessible from within FE code.
    envPrefix: ["REACT_APP_"],
    build: {
      outDir: "build/app",
    },
    server: {
      port: Number(process.env.PORT) || 3000,
      strictPort: true,
      headers: {
        "Content-Security-Policy": "script-src * 'unsafe-inline'; worker-src self blob:;",
      },
    },
    resolve: {
      alias: {
        // Allow @use "scss/" imports in SASS
        scss: path.resolve(__dirname, "./src/scss"),
      },
    },
  };

  return config;
});
