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
    .contains(connectorName)
    .parents("tr")
    .find("[data-testid='version-input']")
    .focus()
    .type(`{selectall} {backspace} ${version}`, { force: true })
    .parents("tr")
    .find("[data-testid='versionButton']")
    .click({ force: true });

  cy.wait(5000);
  cy.get("[data-testid='errorMessage']").should("not.exist");
  cy.get("[data-testid='successMessage']").should("exist");

  // todo: do we want to check that you can upgrade via the button without using the input?
};

export const clickUpgradeAllButton = () => {
  cy.get("[data-testid='upgradeAllButton']").click();
};
