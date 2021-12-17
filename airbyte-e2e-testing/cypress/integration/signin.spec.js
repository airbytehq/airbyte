describe("Signin", () => {
  beforeEach(() => {
    cy.clearApp();
  });

  it("Sign in flow", () => {
    // TODO: replace with signUp()
    cy.signIn("iakov.salikov+100@jamakase.com");

    cy.get("h1[data-testid='onboarding.welcome']");
  });
});
