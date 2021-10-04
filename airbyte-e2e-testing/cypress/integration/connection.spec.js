describe("Connection main actions", () => {
  it("Create new connection", () => {
    cy.createTestConnection("Test connection source cypress", "Test destination cypress");

    cy.get("div").contains("Test connection source cypress").should("exist");
    cy.get("div").contains("Test destination cypress").should("exist");
  });

  it("Update connection", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    cy.createTestConnection("Test update connection source cypress", "Test update connection destination cypress");

    cy.visit("/source");
    cy.get("div").contains("Test update connection source cypress").click();
    cy.get("div").contains("Test update connection destination cypress").click();

    cy.get("div[data-id='settings-step']").click();

    cy.get("div[data-testid='schedule']").click();
    cy.get("div[data-testid='Every 5 min']").click();
    cy.submit();
    cy.wait("@updateConnection");
    cy.get("span[data-id='success-result']").should("exist");

    cy.get("div[data-id='status-step']").click();
    cy.get("div").contains("5 min").should("exist");
});

  it("Delete connection", () => {
    cy.createTestConnection("Test delete connection source cypress", "Test delete connection destination cypress");

    cy.visit("/source");
    cy.get("div").contains("Test delete connection source cypress").click();
    cy.get("div").contains("Test delete connection destination cypress").click();

    cy.get("div[data-id='settings-step']").click();

    cy.deleteEntity();

    cy.deleteSource("Test delete connection source cypress");
    cy.deleteDestination("Test delete connection destination cypress");
  });
});