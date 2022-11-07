const fs = require("fs");
const path = require("path");

const dotenv = require("dotenv");

if (!process.env.AB_ENV) {
  return;
}

const envFile = path.resolve(
  __dirname,
  "../../../airbyte-cloud/cloud-webapp/development",
  `.env.${process.env.AB_ENV}`
);

if (!fs.existsSync(envFile)) {
  console.error(
    `~~~ This mode is for employees only. ~~~\n` +
      `Could not find .env file for environment ${process.env.AB_ENV} (looking at ${envFile}).\n` +
      `Make sure you have the latest airbyte-cloud repository checked out in parallel to the airbyte repository.\n`
  );
  process.exit(42);
}

dotenv.config({ path: envFile });
