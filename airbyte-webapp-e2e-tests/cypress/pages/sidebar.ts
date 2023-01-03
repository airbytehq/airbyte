const setting = "nav a[href*='settings']";
const homepage = "[aria-label='Homepage']";

export const openSettings = () => {
  cy.get(setting).click();
};

export const openHomepage = () => {
  cy.get(homepage).click();
};
