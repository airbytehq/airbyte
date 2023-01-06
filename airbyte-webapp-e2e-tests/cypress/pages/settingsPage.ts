export const goToSettingsSourcesTab = () => {
  cy.intercept("/api/v1/source_definitions/list_for_workspace").as("getSourceDefinitionsList");
  cy.visit("/settings/source");
  cy.wait(5000);
};

export const goToSettingsDestinationTab = () => {
  cy.intercept("/api/v1/destination_definitions/list_for_workspace").as("getDestinationDefinitionsList");
  cy.visit("/settings/destination");
  cy.wait(5000);
};

export const editVersionByConnectorName = (connectorName: string, version: string) => {
  cy.get("[data-testid='connectorNameCell']")
    .contains(connectorName) // div with icon and text
    .parents("tr")
    .find("[data-testid='version-input']")
    .type(`{selectall} {backspace} ${version}`, { force: true });
};

export const clickUpgradeAllButton = () => {
  cy.get("[data-testid='upgradeAllButton']").click();
};
