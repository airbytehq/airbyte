const scheduleDropdown = "div[data-testid='scheduleData']";
const scheduleValue = (value: string) => `div[data-testid='${value}']`;
const destinationPrefix = "input[data-testid='prefixInput']";
const replicationTab = "div[data-id='replication-step']";
const destinationNamespace = "div[data-testid='namespaceDefinition']";
const destinationNamespaceCustom = "div[data-testid='namespaceDefinition-customformat']";
const destinationNamespaceSource = "div[data-testid='namespaceDefinition-source']";
const destinationNamespaceCustomInput = "input[data-testid='input']";
const syncModeDropdown = "div[data-testid='syncSettingsDropdown'] input";
const cursorFieldDropdown = 'button[class^="PathPopoutButton_button"]';
const primaryKeyText = 'div[class^="PathPopout_text"]';
const successResult = "div[data-id='success-result']";
const saveStreamChangesButton = "button[data-testid='resetModal-save']";
const connectionNameInput = "input[data-testid='connectionName']";
const refreshSourceSchemaButton = "button[data-testid='refresh-source-schema-btn']";
const streamSyncEnabledSwitch = (streamName: string) => `[data-testid='${streamName}-stream-sync-switch']`;
const streamNameInput = "input[data-testid='input']";

export const goToReplicationTab = () => {
  cy.get(replicationTab).click();
};

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
  cy.get(destinationNamespaceCustomInput)
    .first()
    .type(value)
    .should("have.value", "${SOURCE_NAMESPACE}" + value);
};

export const setupDestinationNamespaceSourceFormat = () => {
  cy.get(destinationNamespace).click();
  cy.get(destinationNamespaceSource).click();
};

export const refreshSourceSchemaBtnClick = () => {
  cy.get(refreshSourceSchemaButton).click();
};

export const resetModalSaveBtnClick = () => {
  cy.get("[data-testid='resetModal-save']").click();
};

export const selectSyncMode = (source: string, dest: string) => {
    cy.get(syncModeDropdown).first().click({ force: true });

    cy.get(`.react-select__option`) 
        .contains(`Source:${source}| Dest:${dest}`)
        .click();
};

export const selectCursorField = (value: string) => {
    cy.get(cursorFieldDropdown).first().click({ force: true });
  
    cy.get(`.react-select__option`)
        .contains(value)
        .click();
};

export const checkCursorField = (expectedValue: string) => {
    cy.get(cursorFieldDropdown).find('p').should("have.text", expectedValue);
};

export const checkPrimaryKey = (expectedValue: string) => {
    cy.get(primaryKeyText).should("have.text", expectedValue);
};

export const searchStream = (value: string) => {
    cy.get(streamNameInput).type(value);
};

export const checkSuccessResult = () => {
  cy.get(successResult).should("exist");
};

export const confirmStreamConfigurationChangedPopup = () => {
  cy.get(saveStreamChangesButton).click();
};

export const toggleStreamEnabledState = (streamName: string) => {
  cy.get(streamSyncEnabledSwitch(streamName)).check({ force: true });
};
