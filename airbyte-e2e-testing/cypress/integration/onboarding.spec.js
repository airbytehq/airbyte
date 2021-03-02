describe("Onboarding actions", () => {
  it("Skip onboardding", () => {
    cy.visit("/");
    cy.url().should("include", `${Cypress.config().baseUrl}/preferences`);

    // cy.fillEmail("");
    cy.submit();

    cy.url().should("include", `${Cypress.config().baseUrl}/onboarding`);
    cy.get("button[data-id='skip-onboarding']").click();

    cy.url().should("equal", `${Cypress.config().baseUrl}/`);
  });
});
