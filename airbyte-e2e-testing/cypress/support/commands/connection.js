Cypress.Commands.add("createTestConnection", (sourceName, destinationName) => {
  cy.intercept("/api/v1/sources/check_connection").as("checkConnectionSource");
  cy.intercept("/api/v1/destinations/check_connection").as("checkConnectionDestination");

  cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
  cy.intercept("/api/v1/connections/create").as("createConnection");

  cy.createTestSource(sourceName);
  cy.createTestDestination(destinationName);
  cy.wait(3000);

  cy.get("div[role=combobox]").click();
  cy.get("div").contains(sourceName).click();
  cy.wait("@checkConnectionSource");
  cy.wait("@checkConnectionDestination");

  cy.wait("@discoverSchema");

  cy.get("div[data-test-id='frequency']").click();
  cy.get("div[data-id='manual']").click();
  cy.submit();

  cy.wait("@createConnection");
})