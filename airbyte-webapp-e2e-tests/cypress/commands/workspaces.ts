export const initialSetupCompleted = (completed = true) => {
  // Modify the workspaces/list response to mark every workspace as "initialSetupComplete" to ensure we're not showing
  // the setup/preference page for any workspace if this method got called.
  cy.intercept("POST", "/api/v1/workspaces/get", (req) => {
    req.continue((res) => {
      res.body.initialSetupComplete = completed;
      res.send(res.body);
    });
  });

  cy.on("uncaught:exception", (err, runnable) => {
    return false;
  });
};
