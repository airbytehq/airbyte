describe("Restore password", () => {
  beforeEach(() => {
    cy.clearApp();
  });

  it("Restore password flow", () => {
    cy.signUp((email, inboxId) => {
      cy.signOut();
      cy.visit("/login");
      cy.get("a[data-testid='login.forgotPassword']").click();
      cy.get("input[name=email]").type(email);
      cy.get("button[data-testid='login.resetPassword']").click();

      // TODO: optimize waiting for CI
      cy.wait(2500);

      cy.waitForLatestEmail(inboxId).then(({ body }) => {
        cy.visitConfirmationLink(body);
        cy.get("input[name=newPassword]").type(email);
        cy.get("button[data-testid='login.resetPassword']").click();
        cy.signIn(email);
        cy.get("h1[data-testid='onboarding.welcome']");
      });
    });
  });
});
