import {
  addStream,
  configureOffsetPagination,
  enterName,
  enterRecordSelector,
  enterStreamName,
  enterTestInputs,
  enterUrlBase,
  enterUrlPath,
  goToTestPage,
  goToView,
  openTestInputs,
  selectAuthMethod,
  submitForm,
  togglePagination
} from "pages/connectorBuilderPage";

export const configureGlobals = () => {
  goToView("global");
  enterName("Dummy API");
  enterUrlBase("http://dummy_api:6767/");
}

export const configureStream = () => {
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
  enterTestInputs({ apiKey: "theauthkey" })
  submitForm();
}

export const configurePagination = () => {
  goToView("0");
  togglePagination();
  configureOffsetPagination("2", "header", "offset");
}

const testPanelContains = (str: string) => {
  cy.get("pre").contains(str).should("exist");
}

export const assertTestReadAuthFailure = () => {
  testPanelContains('"error": "Bad credentials"');
};

export const assertTestReadItems = () => {
  testPanelContains('"name": "abc"');
  testPanelContains('"name": "def"');
};

export const assertMultiPageReadItems = () => {
  goToTestPage(1);
  assertTestReadItems();

  goToTestPage(2);
  testPanelContains('"name": "xxx"');
  testPanelContains('"name": "yyy"');

  goToTestPage(3);
  testPanelContains('[]');
};