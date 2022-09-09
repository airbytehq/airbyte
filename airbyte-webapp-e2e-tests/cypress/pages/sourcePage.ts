const newSource = "button[data-id='new-source'";

export const goToSourcePage = () => {
  cy.intercept("/api/v1/sources/list").as("getSourcesList");
  cy.visit("/source");
  cy.wait(3000);
  cy.wait("@getSourcesList");
};

export const openSourceDestinationFromGrid = (value: string) => {
  cy.get("div").contains(value).click();
};

export const openNewSourceForm = () => {
  cy.get(newSource).click();
  cy.url().should("include", `/source/new-source`);
};
