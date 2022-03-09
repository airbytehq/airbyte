Cypress.Commands.add("createTestDestination", (name) => {
  cy.intercept("/api/v1/scheduler/destinations/check_connection").as("checkDestinationConnection");
  cy.intercept("/api/v1/destinations/create").as("createDestination");

  cy.openNewDestinationForm();
  cy.fillTestLocalJsonForm(name);
  cy.submitButtonClick();

  cy.wait("@checkDestinationConnection");
  cy.wait("@createDestination");
})

Cypress.Commands.add("updateDestination", (name, field, value) => {
  cy.intercept("/api/v1/destinations/check_connection_for_update").as("checkDestinationUpdateConnection");
  cy.intercept("/api/v1/destinations/update").as("updateDestination");

  cy.openDestinationPage();
  cy.openSettingForm(name);
  cy.updateField(field, value);
  cy.submitButtonClick();

  cy.wait("@checkDestinationUpdateConnection");
  cy.wait("@updateDestination");
})

Cypress.Commands.add("deleteDestination", (name) => {
  cy.openDestinationPage();
  cy.openSettingForm(name);
  cy.deleteEntity();
})