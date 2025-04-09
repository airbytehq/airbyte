import { render } from "cli-testing-library";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * @param {String} script
 * @param {Array} args
 * @param {Object} opts
 */
export function renderScript(script, args = [], opts = {}) {
  const { cwd = __dirname } = opts;

  return render(
    resolve(__dirname, "../node_modules/.bin/nyc"),
    ["--silent", "node", script, ...args],
    {
      cwd,
      spawnOpts: {
        env: { ...process.env, NODE_ENV: "test" },
      },
    }
  );
}

/**
 * @param {Array} args
 * @param {Object} opts
 */
export function renderPlop(args = [], opts = {}) {
  return renderScript(
    resolve(__dirname, "../instrumented/bin/plop.js"),
    args,
    opts
  );
}

export * from "cli-testing-library";
