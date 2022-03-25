Cypress.Commands.add("fillPgSourceForm", (name) => {
  cy.intercept("/api/v1/source_definition_specifications/get").as(
    "getSourceSpecifications"
  );
  
  cy.get("div[data-testid='serviceType']").click();
  cy.get("div").contains("Postgres").click();
  
  cy.wait("@getSourceSpecifications");
  
  cy.get("input[name=name]").type(name);
  cy.get("input[name='connectionConfiguration.host']").type("localhost");
  cy.get("input[name='connectionConfiguration.port']").type("{selectAll}{del}5433");
  cy.get("input[name='connectionConfiguration.database']").type("airbyte_ci");
  cy.get("input[name='connectionConfiguration.username']").type("postgres");
  cy.get("input[name='connectionConfiguration.password']").type(
    "secret_password"
  );
});

Cypress.Commands.add("createTestSource", (name) => {
  cy.intercept("/api/v1/scheduler/sources/check_connection").as(
    "checkSourceUpdateConnection"
  );
  cy.intercept("/api/v1/sources/create").as("createSource");

  cy.openNewSourceForm();
  cy.fillPgSourceForm(name);
  cy.submitButtonClick();

  cy.wait("@checkSourceUpdateConnection");
  cy.wait("@createSource");
});

Cypress.Commands.add("updateSource", (name, field, value) => {
  cy.intercept("/api/v1/sources/check_connection_for_update").as(
    "checkSourceConnection"
  );
  cy.intercept("/api/v1/sources/update").as("updateSource");

  cy.openSourcePage();
  cy.openSettingForm(name);
  cy.updateField(field, value);
  cy.submitButtonClick();

  cy.wait("@checkSourceConnection");
  cy.wait("@updateSource");
});

Cypress.Commands.add("deleteSource", (name) => {
  cy.openSourcePage();
  cy.openSettingForm(name);
  cy.deleteEntity();
});
