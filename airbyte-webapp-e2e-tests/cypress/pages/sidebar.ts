const setting = "nav a[href*='settings']";

export const openSettings = () => {
  cy.get(setting).click();
};
