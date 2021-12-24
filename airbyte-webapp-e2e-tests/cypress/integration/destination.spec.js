describe("Destination main actions", () => {
  it("Create new destination", () => {
    cy.createTestDestination("Test destination cypress");

    cy.url().should("include", `/destination/`);
  });

  it("Update destination", () => {
    cy.createTestDestination("Test destination cypress for update");
    cy.updateDestination("Test destination cypress for update", "connectionConfiguration.destination_path", "/local/my-json");

    cy.get("div[data-id='success-result']").should("exist");
    cy.get("input[value='/local/my-json']").should("exist");
  });

  it("Delete destination", () => {
    cy.createTestDestination("Test destination cypress for delete");
    cy.deleteDestination("Test destination cypress for delete");

    cy.visit("/destination");
    cy.get("div").contains("Test destination cypress for delete").should("not.exist");
  });
});