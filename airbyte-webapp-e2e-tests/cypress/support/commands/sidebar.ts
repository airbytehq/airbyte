Cypress.Commands.add("openSettings", () => {
  cy.get("nav a[href*='settings']").click();
});
