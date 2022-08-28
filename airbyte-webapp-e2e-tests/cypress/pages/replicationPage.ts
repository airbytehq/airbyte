const scheduleDropdown = "div[data-testid='schedule']";
const scheduleValue = "div[data-testid='";
const destinationPrefix = "input[data-testid='prefixInput']";
const replicationTab = "div[data-id='replication-step']";
const destinationNamespace = "div[data-testid='namespaceDefinition']";
const destinationNamespaceCustom = "div[data-testid='namespaceDefinition-customformat']";
const destinationNamespaceSource = "div[data-testid='namespaceDefinition-source']";
const destinationNamespaceCustomInput = "input[data-testid='input']";
const syncModeDropdown = "div[data-testid='syncSettingsDropdown'] input";
const successResult = "span[data-id='success-result']";
const saveStreamChangesButton = "button[data-testid='resetModal-save']";
const connectionNameInput = "input[data-testid='connectionName']";

export const goToReplicationTab = () => {
    cy.get(replicationTab).click();
}

export const enterConnectionName = (name: string) => {
    cy.get(connectionNameInput).type(name);
}

export const selectSchedule = (value: string) => {
    cy.get(scheduleDropdown).click();
    cy.get(scheduleValue + value + "']").click();
}

export const fillOutDestinationPrefix = (value: string) => {
    cy.get(destinationPrefix).clear().type(value).should('have.value', value);;
}

export const setupDestinationNamespaceCustomFormat = (value: string) => {
    cy.get(destinationNamespace).click();
    cy.get(destinationNamespaceCustom).click();
    cy.get(destinationNamespaceCustomInput).first().type(value).should('have.value', '${SOURCE_NAMESPACE}' + value);
}

export const setupDestinationNamespaceSourceFormat = () => {
    cy.get(destinationNamespace).click();
    cy.get(destinationNamespaceSource).click();
}

export const selectFullAppendSyncMode = () => {
  cy.get(syncModeDropdown).first().click({ force: true });

  cy.get(`.react-select__menu`)
    .contains("Append") // it would be nice to select for "Full refresh" is there too
    .click();
};

export const checkSuccessResult = () => {
    cy.get(successResult).should("exist");
}

export const confirmStreamConfigurationChangedPopup = () => {
    cy.get(saveStreamChangesButton).click();
}
