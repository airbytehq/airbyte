import { deleteEntity, openNewSourceForm, openSettingForm, openSourcePage, submitButtonClick, updateField } from "./common";

export const fillPgSourceForm = (name: string) => {
  cy.intercept("/api/v1/source_definition_specifications/get").as(
    "getSourceSpecifications"
  );
  
  cy.get("div[data-testid='serviceType']").click();
  cy.get("div").contains("Postgres").click();
  
  cy.wait("@getSourceSpecifications");
  
  cy.get("input[name=name]").clear().type(name);
  cy.get("input[name='connectionConfiguration.host']").type("localhost");
  cy.get("input[name='connectionConfiguration.port']").type("{selectAll}{del}5433");
  cy.get("input[name='connectionConfiguration.database']").type("airbyte_ci");
  cy.get("input[name='connectionConfiguration.username']").type("postgres");
  cy.get("input[name='connectionConfiguration.password']").type(
    "secret_password"
  );
};

export const createTestSource = (name: string) => {
  cy.intercept("/api/v1/scheduler/sources/check_connection").as(
    "checkSourceUpdateConnection"
  );
  cy.intercept("/api/v1/sources/create").as("createSource");

  openNewSourceForm();
  fillPgSourceForm(name);
  submitButtonClick();

  cy.wait("@checkSourceUpdateConnection");
  cy.wait("@createSource");
};

export const updateSource = (name: string, field: string, value: string) => {
  cy.intercept("/api/v1/sources/check_connection_for_update").as(
    "checkSourceConnection"
  );
  cy.intercept("/api/v1/sources/update").as("updateSource");

  openSourcePage();
  openSettingForm(name);
  updateField(field, value);
  submitButtonClick();

  cy.wait("@checkSourceConnection");
  cy.wait("@updateSource");
}

export const deleteSource = (name: string) => {
  openSourcePage();
  openSettingForm(name);
  deleteEntity();
}
