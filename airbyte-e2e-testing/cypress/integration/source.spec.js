describe("Source main actions", () => {
  before(() => {
    require('./utils.js');
  });

  it("Create new source", () => {
    cy.createTestSource("Test source cypress");

    cy.url().should("include", `${Cypress.config().baseUrl}/source/`);
  });

  it("Update source", () => {
    cy.updateSource("Test source cypress", "connectionConfiguration.start_date", "2020-11-11");

    cy.get("span[data-id='success-result']").should("exist");
    cy.get("input[value='2020-11-11']").should("exist");
  });

  it("Delete source", () => {
    cy.deleteSource("Test source cypress");

    cy.visit("/");
    cy.get("div").contains("Test source cypress").should("not.exist");
  });
});