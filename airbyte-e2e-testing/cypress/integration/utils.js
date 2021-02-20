Cypress.Commands.add("submit", () => {
  cy.get("button[type=submit]").click();
})

Cypress.Commands.add("fillTestExchangeForm", (name) => {
  cy.intercept("/source_definition_specifications/get").as("getSourceSpecifications");

  cy.get("input[name=name]").type(name);
  cy.get("div[role=combobox]").click();
  cy.get("div").contains("Exchange Rates Api").click();

  cy.wait("@getSourceSpecifications");

  cy.get("input[name='connectionConfiguration.base']").type("USD");
  cy.get("input[name='connectionConfiguration.start_date']").type("2020-12-12");
})

Cypress.Commands.add("fillTestLocalJsonForm", (name) => {
  cy.intercept("/destination_definition_specifications/get").as("getDestinationSpecifications");

  cy.get("input[name=name]").type(name);
  cy.get("div[role=combobox]").click();
  cy.get("div").contains("Local JSON").click();

  cy.wait("@getDestinationSpecifications");

  cy.get("input[name='connectionConfiguration.destination_path']").type("/local");
})

Cypress.Commands.add("openSourcePage", () => {
  cy.visit("/");
  cy.intercept("/sources/list").as("getSourcesList");
  cy.wait("@getSourcesList");
})

Cypress.Commands.add("openDestinationPage", () => {
  cy.visit("/destination");
  cy.intercept("/destinations/list").as("getDestinationsList");
  cy.wait("@getDestinationsList");
})

Cypress.Commands.add("openNewSourceForm", () => {
  cy.openSourcePage();
  cy.get("button[data-id='new-source'").click();
  cy.url().should("eq", `${Cypress.config().baseUrl}/source/new-source`);
})

Cypress.Commands.add("openNewDestinationForm", () => {
  cy.openDestinationPage();
  cy.get("button[data-id='new-destination'").click();
  cy.url().should("eq", `${Cypress.config().baseUrl}/destination/new-destination`);
})

Cypress.Commands.add("updateField", (field, value) => {
  cy.get("input[name='" + field + "']").clear().type(value);
})

Cypress.Commands.add("openSettingForm", (name) => {
  cy.get("div").contains(name).click();
  cy.get("div[data-id='settings-step']").click();
})

Cypress.Commands.add("deleteEntity", () => {
  cy.get("button[data-id='open-delete-modal']").click();
  cy.get("button[data-id='delete']").click();
})

// Source actions
Cypress.Commands.add("createTestSource", (name) => {
  cy.intercept("/scheduler/sources/check_connection").as("checkSourceConnection");
  cy.intercept("/sources/create").as("createSource");

  cy.openNewSourceForm();
  cy.fillTestExchangeForm(name);
  cy.submit();

  cy.wait("@checkSourceConnection");
  cy.wait("@createSource");
})

Cypress.Commands.add("updateSource", (name, field, value) => {
  cy.intercept("/sources/check_connection_for_update").as("checkSourceConnection");
  cy.intercept("/sources/update").as("updateSource");

  cy.openSourcePage();
  cy.openSettingForm(name);
  cy.updateField(field, value);
  cy.submit();

  cy.wait("@checkSourceConnection");
  cy.wait("@updateSource");
})

Cypress.Commands.add("deleteSource", (name) => {
  cy.openSourcePage();
  cy.openSettingForm(name);
  cy.deleteEntity();
})

// Destination actions
Cypress.Commands.add("createTestDestination", (name) => {
  cy.intercept("/scheduler/destinations/check_connection").as("checkDestinationConnection");
  cy.intercept("/destinations/create").as("createDestination");

  cy.openNewDestinationForm();
  cy.fillTestLocalJsonForm(name);
  cy.submit();

  cy.wait("@checkDestinationConnection");
  cy.wait("@createDestination");
})

Cypress.Commands.add("updateDestination", (name, field, value) => {
  cy.intercept("/destinations/check_connection_for_update").as("checkDestinationConnection");
  cy.intercept("/destinations/update").as("updateDestination");

  cy.openDestinationPage();
  cy.openSettingForm(name);
  cy.updateField(field, value);
  cy.submit();

  cy.wait("@checkDestinationConnection");
  cy.wait("@updateDestination");
})

Cypress.Commands.add("deleteDestination", (name) => {
  cy.openDestinationPage();
  cy.openSettingForm(name);
  cy.deleteEntity();
  })