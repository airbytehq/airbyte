const fs = require("fs");
const path = require("path");

const EXPERIMENTS_FILE = path.resolve(__dirname, "../.experiments.json");

if (fs.existsSync(EXPERIMENTS_FILE)) {
  console.log("\nOverwriting experiments from .experiments.json ...");
  const overwrites = require(EXPERIMENTS_FILE);

  if (Object.keys(overwrites).length) {
    console.log(`Overwriting experiments with the following values:\n\n${JSON.stringify(overwrites, null, 2)}`);
    process.env.REACT_APP_EXPERIMENT_OVERWRITES = JSON.stringify(overwrites);
  }
}
