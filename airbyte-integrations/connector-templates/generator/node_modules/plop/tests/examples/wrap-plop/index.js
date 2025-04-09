#!/usr/bin/env node
import path from "node:path";
import minimist from "minimist";
import { Plop, run } from "../../../instrumented/src/plop.js";

const args = process.argv.slice(2);
const argv = minimist(args);
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

Plop.prepare(
  {
    cwd: argv.cwd,
    preload: argv.preload || [],
    // In order for `plop` to always pick up the `plopfile.js` despite the CWD, you must use `__dirname`
    configPath: path.join(__dirname, "plopfile.cjs"),
    completion: argv.completion,
    // This will merge the `plop` argv and the generator argv.
    // This means that you don't need to use `--` anymore
  },
  function (env) {
    Plop.execute(env, function (env) {
      return run(env, undefined, true);
    });
  }
);
