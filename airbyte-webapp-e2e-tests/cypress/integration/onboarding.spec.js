describe("Preferences actions", () => {
  it("Should redirect to onboarding after email is entered", () => {
    cy.visit("/preferences");
    cy.url().should("include", `/preferences`);

    cy.fillEmail("test-email-onboarding@test-onboarding-domain.com");
    cy.get("input[name=securityUpdates]").parent().click();

    cy.submitButtonClick();

    cy.url().should("match", /.*\/onboarding/);
  });
});
