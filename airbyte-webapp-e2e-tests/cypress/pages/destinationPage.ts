const newDestination = "button[data-id='new-destination']";
const addSourceButton = "button[data-testid='select-source']";

export const goToDestinationPage = () => {
  cy.intercept("/api/v1/destinations/list").as("getDestinationsList");
  cy.visit("/destination");
  cy.wait(3000);
};

export const openNewDestinationForm = () => {
  cy.wait("@getDestinationsList").then(({ response }) => {
    if (response?.body.destinations.length) {
      cy.get(newDestination).click();
    }
  });
  cy.url().should("include", `/destination/new-destination`);
};

export const openAddSource = () => {
  cy.get(addSourceButton).click();
};
