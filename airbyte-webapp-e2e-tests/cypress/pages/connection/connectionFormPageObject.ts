const scheduleDropdown = "div[data-testid='scheduleData']";
const scheduleValue = (value: string) => `div[data-testid='${value}']`;
const destinationPrefix = "input[data-testid='prefixInput']";
const destinationNamespace = "div[data-testid='namespaceDefinition']";
const destinationNamespaceCustom = "div[data-testid='namespaceDefinition-customformat']";
const destinationNamespaceDefault = "div[data-testid='namespaceDefinition-destination']";
const destinationNamespaceSource = "div[data-testid='namespaceDefinition-source']";
const destinationNamespaceCustomInput = "input[data-testid='input']";
const connectionNameInput = "input[data-testid='connectionName']";

export const enterConnectionName = (name: string) => {
  cy.get(connectionNameInput).type(name);
};

export const selectSchedule = (value: string) => {
  cy.get(scheduleDropdown).click();
  cy.get(scheduleValue(value)).click();
};

export const fillOutDestinationPrefix = (value: string) => {
  cy.get(destinationPrefix).clear().type(value).should("have.value", value);
};

export const setupDestinationNamespaceCustomFormat = (value: string) => {
  cy.get(destinationNamespace).click();
  cy.get(destinationNamespaceCustom).click();
  cy.get(destinationNamespaceCustomInput).first().type(value).should("have.value", `\${SOURCE_NAMESPACE}${value}`);
};

export const setupDestinationNamespaceSourceFormat = () => {
  cy.get(destinationNamespace).click();
  cy.get(destinationNamespaceSource).click();
};

export const setupDestinationNamespaceDefaultFormat = () => {
  cy.get(destinationNamespace).click();
  cy.get(destinationNamespaceDefault).click();
};
