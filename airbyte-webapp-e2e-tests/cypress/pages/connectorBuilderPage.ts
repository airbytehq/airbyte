const nameInput = "input[name=global.connectorName]";
const urlBaseInput = "input[name=global.urlBase]";
const addStreamButton = "button[data-testid=add-stream]";

const streamNameInput = "input[name=streamName]";
const streamUrlPath = "input[name=urlPath]";

const submit = "button[type=submit]"

const testStreamButton = "button[data-testid=read-stream]";

export const goToConnectorBuilderPage = () => {
  cy.visit("/connector-builder");
  cy.wait(3000);
};

export const enterName = (name: string) => {
  cy.get(nameInput).clear().type(name);
};

export const enterUrlBase = (urlBase: string) => {
  cy.get(urlBaseInput).clear().type(urlBase);
};

export const addStream = () => {
  cy.get(addStreamButton).click();
};

export const enterStreamName = (streamName: string) => {
  cy.get(streamNameInput).clear().type(streamName);
};

export const enterUrlPath = (urlPath: string) => {
  cy.get(streamUrlPath).clear().type(urlPath);
};

export const submitForm = () => {
  cy.get(submit).click();
};

export const testStream = () => {
  cy.get(testStreamButton).click();
};