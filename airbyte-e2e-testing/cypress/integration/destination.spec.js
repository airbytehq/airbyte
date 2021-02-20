describe("Destination main actions", () => {
  before(() => {
    require('./utils.js');
  });

  it("Create new destination", () => {
    cy.createTestDestination("Test destination cypress");

    cy.url().should("include", `${Cypress.config().baseUrl}/destination/`);
  });

  it("Update destination", () => {
    cy.updateDestination("Test destination cypress", "connectionConfiguration.destination_path", "/local/my-json");

    cy.get("span[data-id='success-result']").should("exist");
    cy.get("input[value='/local/my-json']").should("exist");
  });

  it("Delete destination", () => {
    cy.deleteDestination("Test destination cypress");

    cy.visit("/destination");
    cy.get("div").contains("Test destination cypress").should("not.exist");
  });
});