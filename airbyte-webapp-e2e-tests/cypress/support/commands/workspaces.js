Cypress.Commands.add("initialSetupCompleted", (completed = true) => {
  // Modify the workspaces/list response to mark every workspace as "initialSetupComplete" to ensure we're not showing
  // the setup/preference page for any workspace if this method got called.
  cy.intercept("POST", "/api/v1/workspaces/list", (req) => {
    req.continue(res => {
      res.body.workspaces = res.body.workspaces.map(ws => ({ ...ws, initialSetupComplete: completed }));
      res.send(res.body);
    });
  });
});
