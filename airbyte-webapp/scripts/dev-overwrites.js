const fs = require("fs");
const { isMainThread } = require("node:worker_threads");
const path = require("path");

const chalk = require("chalk");

const EXPERIMENTS_FILE = path.resolve(__dirname, "../.experiments.json");

if (fs.existsSync(EXPERIMENTS_FILE)) {
  const overwrites = require(EXPERIMENTS_FILE);

  if (Object.keys(overwrites).length) {
    if (isMainThread) {
      // Only print the message in the main thread, so it's not showing up in all the worker threads of vite-plugin-checker
      console.log(chalk.bold(`🧪 Overwriting experiments via ${chalk.green(".experiments.json")}`));
      Object.entries(overwrites).forEach(([key, value]) => {
        console.log(`   ➜ ${chalk.cyan(key)}: ${JSON.stringify(value)}`);
      });
    }
    process.env.REACT_APP_EXPERIMENT_OVERWRITES = JSON.stringify(overwrites);
  }
}
