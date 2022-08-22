const scheduleDropdown = "div[data-testid='schedule']";
const scheduleValue = "div[data-testid='";
const destinationPrefix = "input[data-testid='prefixInput']";
const replicationTab = "div[data-id='replication-step']";
const destinationNamespace = "div[data-testid='namespaceDefinition']";
const destinationNamespaceCustom = "div[data-testid='namespaceDefinition-customformat']";
const destinationNamespaceCustomInput = "input[data-testid='input']";
const syncModeDropdown = "div.sc-lbxAil.hgSxej";
const syncModeFullAppendValue = "div.sc-ftvSup.sc-jDDxOa.sEMqZ.kVUvAu";
const successResult = "span[data-id='success-result']";
const saveChangesButton = "button[type=submit]";
const saveStreamChangesButton = "button[data-testid='resetModal-save']";

export const goToReplicationTab = () => {
    cy.get(replicationTab).click();
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

export const selectFullAppendSyncMode = () => {
    cy.get(syncModeDropdown).click();
    cy.get(syncModeFullAppendValue).click();
}

export const checkSuccessResult = () => {
    cy.get(successResult).should("exist");
}

export const clickSaveChanges = () => {
    cy.get(saveChangesButton).first().click();
}

export const confirmStreamConfigurationChangedPopup = () => {
    cy.get(saveStreamChangesButton).click();
}
