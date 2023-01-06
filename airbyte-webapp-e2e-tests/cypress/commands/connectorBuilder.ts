import { addStream, configureOffsetPagination, enterName, enterRecordSelector, enterStreamName, enterTestInputs, enterUrlBase, enterUrlPath, goToTestPage, goToView, openTestInputs, selectAuthMethod, submitForm, togglePagination } from "pages/connectorBuilderPage";

export const configureGlobals = () => {
  goToView("global");
  enterName("Dummy API");
  enterUrlBase("http://dummy_api:6767/");
}

export const configureStreamWithoutAuth = () => {
  addStream();
  enterStreamName("Items");
  enterUrlPath("items/");
  submitForm();
  enterRecordSelector("items");
}

export const configureAuth = () => {
  goToView("global");
  selectAuthMethod("Bearer");
  openTestInputs();
  enterTestInputs({ apiKey: "theauthkey"})
  submitForm();
}

export const configurePagination = () => {
 goToView("0");
 togglePagination();
 configureOffsetPagination("2", "header", "offset");
}

export const assertTestReadAuthFailure = () => {
    cy.get("pre").contains('"error": "Bad credentials"').should("exist");
};

export const assertTestReadItems = () => {
    cy.get("pre").contains('"name": "abc"').should("exist");
    cy.get("pre").contains('"name": "def"').should("exist");
};

export const assertMultiPageReadItems = () => {
  goToTestPage(1);
  cy.get("pre").contains('"name": "abc"').should("exist");
  cy.get("pre").contains('"name": "def"').should("exist");
  goToTestPage(2);
  cy.get("pre").contains('"name": "xxx"').should("exist");
  cy.get("pre").contains('"name": "yyy"').should("exist");
  goToTestPage(3);
  cy.get("pre").contains('[]').should("exist");
};