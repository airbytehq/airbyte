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
  cy.intercept("/destinations/check_connection_for_update").as("checkDestinationUpdateConnection");
  cy.intercept("/destinations/update").as("updateDestination");

  cy.openDestinationPage();
  cy.openSettingForm(name);
  cy.updateField(field, value);
  cy.submit();

  cy.wait("@checkDestinationUpdateConnection");
  cy.wait("@updateDestination");
})

Cypress.Commands.add("deleteDestination", (name) => {
  cy.openDestinationPage();
  cy.openSettingForm(name);
  cy.deleteEntity();
})