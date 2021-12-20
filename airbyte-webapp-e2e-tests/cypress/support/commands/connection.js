Cypress.Commands.add("createTestConnection", (sourceName, destinationName) => {
  cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
  cy.intercept("/api/v1/web_backend/connections/create").as("createConnection");

  cy.createTestSource(sourceName);
  cy.createTestDestination(destinationName);
  cy.wait(3000);

  cy.get("div[data-testid='select-source']").click();
  cy.get("div").contains(sourceName).click();

  cy.wait("@discoverSchema");

  cy.get("div[data-testid='schedule']").click();
  cy.get("div[data-testid='manual']").click();
  cy.submit();

  cy.wait("@createConnection");
});
