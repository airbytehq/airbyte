describe("Signup", () => {
  beforeEach(() => {
    cy.clearApp();
  });

  it("Sign up flow", async () => {
    cy.signUp(() => {
      cy.get("h1[data-testid='onboarding.welcome']");
    });
  });
});
