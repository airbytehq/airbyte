export const submitButtonClick = () => {
  cy.get("button[type=submit]").click();
}

export const fillEmail = (email: string) => {
  cy.get("input[name=email]").type(email);
}

export const fillTestLocalJsonForm = (name: string) => {
  cy.intercept("/api/v1/destination_definition_specifications/get").as("getDestinationSpecifications");

  cy.get("div[data-testid='serviceType']").click();
  cy.get("div").contains("Local JSON").click();
  
  cy.wait("@getDestinationSpecifications");
  
  cy.get("input[name=name]").clear().type(name);
  cy.get("input[name='connectionConfiguration.destination_path']").type("/local");
}

export const openSourcePage = () => {
  cy.intercept("/api/v1/sources/list").as("getSourcesList");
  cy.visit("/source");
  cy.wait("@getSourcesList");
}

export const openDestinationPage = () => {
  cy.intercept("/api/v1/destinations/list").as("getDestinationsList");
  cy.visit("/destination");
  cy.wait("@getDestinationsList");
}

export const openNewSourceForm = () => {
  openSourcePage();
  cy.get("button[data-id='new-source'").click();
  cy.url().should("include", `/source/new-source`);
}

export const openNewDestinationForm = () => {
  openDestinationPage();
  cy.get("button[data-id='new-destination'").click();
  cy.url().should("include", `/destination/new-destination`);
}

export const updateField = (field: string, value: string) => {
  cy.get("input[name='" + field + "']").clear().type(value);
}

export const openSettingForm = (name: string) => {
  cy.get("div").contains(name).click();
  cy.get("div[data-id='settings-step']").click();
}

export const deleteEntity = () => {
  cy.get("button[data-id='open-delete-modal']").click();
  cy.get("button[data-id='delete']").click();
}

export const clearApp = () => {
  indexedDB.deleteDatabase("firebaseLocalStorageDb");
  cy.clearLocalStorage();
  cy.clearCookies();
}
