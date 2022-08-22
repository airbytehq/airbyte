export const openSettings = () => {
  cy.get("nav a[href*='settings']").click();
};
