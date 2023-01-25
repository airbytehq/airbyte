import { deleteEntity, openSettingForm, submitButtonClick, updateField } from "./common";
import { goToSourcePage, openNewSourceForm } from "pages/sourcePage";
import { fillPostgresForm, fillPokeAPIForm } from "./connector";

export const createPostgresSource = (
  name: string,
  host = "localhost",
  port = "5433",
  database = "airbyte_ci_source",
  username = "postgres",
  password = "secret_password",
  schema = ""
) => {
  cy.intercept("/api/v1/scheduler/sources/check_connection").as("checkSourceUpdateConnection");
  cy.intercept("/api/v1/sources/create").as("createSource");

  goToSourcePage();
  openNewSourceForm();
  fillPostgresForm(name, host, port, database, username, password, schema);
  submitButtonClick();

  cy.wait("@checkSourceUpdateConnection", { requestTimeout: 10000 });
  cy.wait("@createSource");
};

export const createPokeApiSource = (name: string, pokeName: string) => {
  cy.intercept("/api/v1/scheduler/sources/check_connection").as("checkSourceUpdateConnection");
  cy.intercept("/api/v1/sources/create").as("createSource");

  goToSourcePage();
  openNewSourceForm();
  fillPokeAPIForm(name, pokeName);
  submitButtonClick();

  cy.wait("@checkSourceUpdateConnection");
  cy.wait("@createSource");
};

export const updateSource = (name: string, field: string, value: string) => {
  cy.intercept("/api/v1/sources/check_connection_for_update").as("checkSourceConnection");
  cy.intercept("/api/v1/sources/update").as("updateSource");

  goToSourcePage();
  openSettingForm(name);
  updateField(field, value);
  submitButtonClick();

  cy.wait("@checkSourceConnection");
  cy.wait("@updateSource");
};

export const deleteSource = (name: string) => {
  cy.intercept("/api/v1/sources/delete").as("deleteSource");
  goToSourcePage();
  openSettingForm(name);
  deleteEntity();
  cy.wait("@deleteSource");
};
