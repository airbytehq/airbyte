const fs = require("fs");
const path = require("path");

const dotenv = require("dotenv");

function parseFromString(value) {
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  if (value.startsWith("[") || value.startsWith("{")) {
    return JSON.parse(value);
  }

  return value;
}

const EXPERIMENTS_FILE = path.resolve(__dirname, "../.experiments.dev");

if (fs.existsSync(EXPERIMENTS_FILE)) {
  console.log("\nOverwriting experiments from .experiments.dev ...");
  const rawOverwrites = dotenv.parse(fs.readFileSync(EXPERIMENTS_FILE));
  const overwrites = Object.fromEntries(
    Object.entries(rawOverwrites).map(([key, value]) => {
      return [key, parseFromString(value)];
    })
  );

  if (Object.keys(overwrites).length) {
    console.log(`Overwriting experiments with the following values:\n\n${JSON.stringify(overwrites, null, 2)}`);
    process.env.REACT_APP_EXPERIMENT_OVERWRITES = JSON.stringify(overwrites);
  }
}

const FEATURES_FILE = path.resolve(__dirname, "../.features.dev");

if (fs.existsSync(FEATURES_FILE)) {
  console.log("\nOverwriting feature states from .features.dev ...");
  const overwrites = dotenv.parse(fs.readFileSync(FEATURES_FILE));
  Object.entries(overwrites).forEach(([key, value]) => {
    console.log(`Overwrite feature ${key} with value ${value}`);
    process.env[`REACT_APP_FEATURE_${key}`] = value;
  });
}
