describe("Workspace", async () => {
  let name = Math.random();

  before(() => {
    cy.clearApp();
    cy.signIn("iakov.salikov+100@jamakase.com");
    name = Math.random();
  });

  describe("Create workspace", async () => {
    it("should be existed workspaces", () => {
      cy.createWorkspace(name);
      cy.wait(5000);
      cy.get("h5").contains(name).click();
      cy.get("div").contains(name);
    });
  });

  describe("Rename workspace", async () => {
    it("should be renamed workspace", () => {
      cy.renameWorkspace(Math.random());

      cy.get("#root > div > nav > div > div").click();
      cy.get("span").contains(name);
    });
  });

  describe("Remove workspace", async () => {
    it("should be what ???", () => {
      cy.removeWorkspace();
    });
  });
});
