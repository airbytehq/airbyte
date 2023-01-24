import path from "path";

import basicSsl from "@vitejs/plugin-basic-ssl";
import react from "@vitejs/plugin-react";
import { loadEnv, UserConfig } from "vite";
import { defineConfig } from "vite";
import checker from "vite-plugin-checker";
import svgrPlugin from "vite-plugin-svgr";
import viteTsconfigPaths from "vite-tsconfig-paths";

import { docMiddleware, patchReactVirtualized } from "./packages/vite-plugins";

export default defineConfig(({ mode }) => {
  // Load variables from all .env files
  process.env = {
    ...process.env,
    ...loadEnv(mode, __dirname, ""),
  };

  // Environment variables that should be available in the frontend
  const frontendEnvVariables = loadEnv(mode, __dirname, ["REACT_APP_"]);
  // Create an object of defines that will shim all required process.env variables.
  const processEnv = {
    "process.env.NODE_ENV": JSON.stringify(mode),
    ...Object.fromEntries(
      Object.entries(frontendEnvVariables).map(([key, value]) => [`process.env.${key}`, JSON.stringify(value)])
    ),
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
          badgeStyle: "transform: translate(-135px,-11px)",
        },
        eslint: { lintCommand: `eslint --max-warnings=0 --ext js,ts,tsx src` },
        stylelint: {
          lintCommand: 'stylelint "src/**/*.{css,scss}"',
          // We need to overwrite this during development, since otherwise `files` are wrongly
          // still containing the quotes around them, which they shouldn't
          dev: { overrideConfig: { files: "src/**/*.{css,scss}" } },
        },
        typescript: true,
      }),
      patchReactVirtualized(),
      docMiddleware(),
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
    define: {
      ...processEnv,
    },
    css: {
      modules: {
        generateScopedName: "[name]__[local]__[contenthash:6]",
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
