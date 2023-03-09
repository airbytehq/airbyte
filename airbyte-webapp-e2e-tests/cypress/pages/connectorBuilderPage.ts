const nameInput = "input[name='global.connectorName']";
const urlBaseInput = "input[name='global.urlBase']";
const addStreamButton = "button[data-testid='add-stream']";
const apiKeyInput = "input[name='connectionConfiguration.api_key']";
const toggleInput = "input[data-testid='toggle']";
const streamNameInput = "input[name='streamName']";
const streamUrlPath = "input[name='urlPath']";
const recordSelectorInput = "[data-testid='tag-input'] input";
const authType = "[data-testid='global.authenticator.type']";
const testInputsButton = "[data-testid='test-inputs']";
const limitInput = "[name='streams[0].paginator.strategy.page_size']";
const injectOffsetInto = "[data-testid$='paginator.pageTokenOption.inject_into']";
const injectOffsetFieldName = "[name='streams[0].paginator.pageTokenOption.field_name']";
const testPageItem = "[data-testid='test-pages'] li";
const submit = "button[type='submit']"
const testStreamButton = "button[data-testid='read-stream']";

export const goToConnectorBuilderPage = () => {
  cy.visit("/connector-builder");
  cy.wait(3000);
};

export const enterName = (name: string) => {
  cy.get(nameInput).type(name);
};

export const enterUrlBase = (urlBase: string) => {
  cy.get(urlBaseInput).type(urlBase);
};

export const enterRecordSelector = (recordSelector: string) => {
  cy.get(recordSelectorInput).first().type(recordSelector, { force: true }).type("{enter}", { force: true });
};

const selectFromDropdown = (selector: string, value: string) => {
  cy.get(`${selector} .react-select__dropdown-indicator`).last().click({ force: true });

  cy.get(`.react-select__option`).contains(value).click();
}

export const selectAuthMethod = (value: string) => {
  selectFromDropdown(authType, value);
};

export const goToView = (view: string) => {
  cy.get(`button[data-testid=navbutton-${view}]`).click();
}

export const openTestInputs = () => {
  cy.get(testInputsButton).click();
}

export const enterTestInputs = ({ apiKey }: { apiKey: string }) => {
  cy.get(apiKeyInput).type(apiKey);
}

export const goToTestPage = (page: number) => {
  cy.get(testPageItem).contains(page).click();
}

export const togglePagination = () => {
  cy.get(toggleInput).first().click({ force: true });
}

export const configureOffsetPagination = (limit: string, into: string, fieldName: string) => {
  cy.get(limitInput).type(limit);
  selectFromDropdown(injectOffsetInto, into);
  cy.get(injectOffsetFieldName).type(fieldName);
}

export const addStream = () => {
  cy.get(addStreamButton).click();
};

export const enterStreamName = (streamName: string) => {
  cy.get(streamNameInput).type(streamName);
};

export const enterUrlPath = (urlPath: string) => {
  cy.get(streamUrlPath).type(urlPath);
};

export const submitForm = () => {
  cy.get(submit).click();
};

export const testStream = () => {
  // wait for debounced form
  cy.wait(500);
  cy.get(testStreamButton).click();
};