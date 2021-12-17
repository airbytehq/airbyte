describe("Signuot", () => {
  beforeEach(() => {
    cy.clearApp();
  });

  it("Sign out flow", () => {
    // TODO: replace with signUp()
    cy.signIn("iakov.salikov+100@jamakase.com");
    cy.signOut();

    cy.get("h1[data-testid='login.loginTitle']");
  });
});
