Cypress.Commands.add("createTestSource", (name) => {
  cy.intercept("/scheduler/sources/check_connection").as("checkSourceUpdateConnection");
  cy.intercept("/sources/create").as("createSource");

  cy.openNewSourceForm();
  cy.fillTestExchangeForm(name);
  cy.submit();

  cy.wait("@checkSourceUpdateConnection");
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
