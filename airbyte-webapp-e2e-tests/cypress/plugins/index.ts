/// <reference types="cypress" />
// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

import Cypress from "cypress";

const pgp = require("pg-promise")();
const cypressConfig = require(require("path").resolve("cypress.json"));

interface dbConfig {
  user: string;
  host: string;
  database: string;
  password: string;
  port: number;
}

function dbConnection(query: any, userDefineConnection: dbConfig) {
  let connection = cypressConfig.db;
  if (userDefineConnection !== undefined) {
    connection = userDefineConnection;
  }
  const db = pgp(connection);
  return db.any(query).finally(db.$pool.end);
}

/**
 * @type {Cypress.PluginConfig}
 */
module.exports = (on: Cypress.PluginEvents, config: Cypress.PluginConfigOptions) => {
  // `on` is used to hook into various events Cypress emits
  // `config` is the resolved Cypress config
  on("task", {
    dbQuery: (query) => dbConnection(query.query, query.connection),
  });
};
