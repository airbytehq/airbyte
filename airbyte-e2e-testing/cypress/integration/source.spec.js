describe("Source main actions", () => {
  it("Create new source", () => {
    cy.createTestSource("Test source cypress");

    cy.url().should("include", `/source/`);
  });

  //TODO: add update source on some other connector or create 1 more user for pg
  it.skip("Update source", () => {
    cy.createTestSource("Test source cypress for update");
    cy.updateSource("Test source cypress for update", "connectionConfiguration.start_date", "2020-11-11");

    cy.get("div[data-id='success-result']").should("exist");
    cy.get("input[value='2020-11-11']").should("exist");
  });

  it("Delete source", () => {
    cy.createTestSource("Test source cypress for delete");
    cy.deleteSource("Test source cypress for delete");

    cy.visit("/");
    cy.get("div").contains("Test source cypress for delete").should("not.exist");
  });
});