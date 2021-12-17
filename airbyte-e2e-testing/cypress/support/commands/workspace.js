Cypress.Commands.add("openWorkspace", (name) => {
  cy.get("nav > div > div").click();
  cy.get("div").contains(name).click();
  cy.wait(3000);
});

Cypress.Commands.add("createWorkspace", (name) => {
  cy.get("div[data-testid='sidebar.workspaceButton']").click();
  cy.get("div[data-testid='workspaces.viewAllWorkspaces']").click();
  cy.wait(500);
  cy.get("button[data-testid='workspaces.createNew']").click();
  cy.get("input[name=name]").type(name);
  cy.get("button[data-testid='workspaces.create']").click();
  cy.wait(1000);
});

Cypress.Commands.add("renameWorkspace", (name) => {
  cy.openSettings();

  cy.get("div[data-testid='workspaceSettings.generalSettings']").click({
    force: true,
  });

  cy.get("input[name=name]").type(name);
  cy.get("button[type=submit]").click();
});

Cypress.Commands.add("removeWorkspace", () => {
  cy.openSettings();

  cy.get("div[data-testid='workspaceSettings.generalSettings']").click({
    force: true,
  });

  cy.get("button[data-testid='generalSettings.deleteWorkspace']").click({
    force: true,
  });
});
