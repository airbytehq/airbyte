const nameInput = "input[name='global.connectorName']";
const urlBaseInput = "input[name='global.urlBase']";
const addStreamButton = "button[data-testid='add-stream']";
const apiKeyInput = "input[name='connectionConfiguration.api_key']";
const toggleInput = "input[data-testid='toggle']";

const streamNameInput = "input[name='streamName']";
const streamUrlPath = "input[name='urlPath']";
const recordSelectorInput = "[data-testid='tag-input'] input";
const authType = "[data-testid='global.authenticator.type'] .react-select__dropdown-indicator";
const testInputsButton = "[data-testid='test-inputs']";
const limitInput = "[name='streams[0].paginator.strategy.page_size']";
const injectOffsetInto = "[data-testid='streams[0].paginator.pageTokenOption.inject_into']  .react-select__dropdown-indicator";
const injectOffsetFieldName = "[name='streams[0].paginator.pageTokenOption.field_name']";

const testPageItem = "[data-testid='test-pages'] li";

const submit = "button[type='submit']"

const testStreamButton = "button[data-testid='read-stream']";

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

export const enterRecordSelector = (recordSelector: string) => {
  cy.get(recordSelectorInput).first().type(recordSelector, { force: true }).type("{enter}", { force: true });
};

export const selectAuthMethod = (value: string) => {
  cy.get(authType).last().click({ force: true });

  cy.get(`.react-select__option`).contains(value).click();
};

export const goToView = (view: string) => {
  cy.get(`button[data-testid=navbutton-${view}]`).click();
}

export const openTestInputs = () => {
  cy.get(testInputsButton).click();
}

export const enterTestInputs = ({ apiKey }: { apiKey: string }) => {
  cy.get(apiKeyInput).clear().type(apiKey);
}

export const goToTestPage = (page: number) => {
  cy.get(testPageItem).contains(page).click();
}

export const togglePagination = () => {
  cy.get(toggleInput).first().click({ force: true });
}

export const configureOffsetPagination = (limit: string, into: string, fieldName: string) => {
  cy.get(limitInput).clear().type(limit);
  cy.get(injectOffsetInto).last().click({ force: true });

  cy.get(`.react-select__option`).contains(into).click();
  cy.get(injectOffsetFieldName).clear().type(fieldName);
  // wait for debounced form
  cy.wait(250);
}

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