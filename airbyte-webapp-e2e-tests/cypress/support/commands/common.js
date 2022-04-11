Cypress.Commands.add("submitButtonClick", () => {
  cy.get("button[type=submit]").click();
})

Cypress.Commands.add("fillEmail", (email) => {
  cy.get("input[name=email]").type(email);
})

Cypress.Commands.add("fillTestLocalJsonForm", (name) => {
  cy.intercept("/api/v1/destination_definition_specifications/get").as("getDestinationSpecifications");

  cy.get("div[data-testid='serviceType']").click();
  cy.get("div").contains("Local JSON").click();
  
  cy.wait("@getDestinationSpecifications");
  
  cy.get("input[name=name]").type(name);
  cy.get("input[name='connectionConfiguration.destination_path']").type("/local");
})

Cypress.Commands.add("openSourcePage", () => {
  cy.intercept("/api/v1/sources/list").as("getSourcesList");
  cy.visit("/source");
  cy.wait("@getSourcesList");
})

Cypress.Commands.add("openDestinationPage", () => {
  cy.intercept("/api/v1/destinations/list").as("getDestinationsList");
  cy.visit("/destination");
  cy.wait("@getDestinationsList");
})

Cypress.Commands.add("openNewSourceForm", () => {
  cy.openSourcePage();
  cy.get("button[data-id='new-source'").click();
  cy.url().should("include", `/source/new-source`);
})

Cypress.Commands.add("openNewDestinationForm", () => {
  cy.openDestinationPage();
  cy.get("button[data-id='new-destination'").click();
  cy.url().should("include", `/destination/new-destination`);
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

Cypress.Commands.add("clearApp", () => {
  indexedDB.deleteDatabase("firebaseLocalStorageDb");
  cy.clearLocalStorage();
  cy.clearCookies();
});
