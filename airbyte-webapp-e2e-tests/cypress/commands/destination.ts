import { deleteEntity, fillTestLocalJsonForm, openDestinationPage, openNewDestinationForm, openSettingForm, submitButtonClick, updateField } from "./common";

export const createTestDestination = (name: string) => {
  cy.intercept("/api/v1/scheduler/destinations/check_connection").as("checkDestinationConnection");
  cy.intercept("/api/v1/destinations/create").as("createDestination");

  openNewDestinationForm();
  fillTestLocalJsonForm(name);
  submitButtonClick();

  cy.wait("@checkDestinationConnection");
  cy.wait("@createDestination");
}

export const updateDestination = (name: string, field: string, value: string) => {
  cy.intercept("/api/v1/destinations/check_connection_for_update").as("checkDestinationUpdateConnection");
  cy.intercept("/api/v1/destinations/update").as("updateDestination");

  openDestinationPage();
  openSettingForm(name);
  updateField(field, value);
  submitButtonClick();

  cy.wait("@checkDestinationUpdateConnection");
  cy.wait("@updateDestination");
}

export const deleteDestination = (name: string) => {
  openDestinationPage();
  openSettingForm(name);
  deleteEntity();
}