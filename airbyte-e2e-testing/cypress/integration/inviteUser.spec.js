describe("Invite user", () => {
  beforeEach(() => {
    cy.clearApp();
  });

  it("Invite user flow", () => {
    cy.signUp((email) => {
      cy.signOut();

      // TODO: replace with signUp()
      cy.signIn("iakov.salikov+100@jamakase.com");

      // TODO: optimize waiting for CI
      cy.wait(5000);

      cy.openSettings();
      cy.get(
        "div[data-testid='workspaceSettings.accessManagementSettings']"
      ).click();
      cy.get("button[data-testid='userSettings.button.addNewUser']").click();
      cy.get("input[name='users[0].email']").type(email);
      cy.get("button[data-testid='modals.addUser.button.submit']").click();
    });
  });
});
