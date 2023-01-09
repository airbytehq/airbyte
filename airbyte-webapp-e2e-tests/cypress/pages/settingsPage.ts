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

export const editVersionByConnectorName = (
  connectorType: "source" | "destination",
  connectorId: string,
  version?: string
) => {
  cy.intercept(`/api/v1/${connectorType}_definitions/update`).as("updateConnectorDefinitions");

  if (version) {
    cy.get(`[data-testid='${connectorId}-versionInput']`).clear().wait(1000);
    cy.get(`[data-testid='${connectorId}-versionInput']`).type(`${version}`).wait(1000);
  }

  cy.get(`[data-testid='${connectorId}-versionButton']`).click();
  cy.wait("@updateConnectorDefinitions");

  cy.get("[data-testid='errorMessage']").should("not.exist");
  cy.get("[data-testid='successMessage']").should("exist");

  // todo: do we want to check that you can upgrade via the button without using the input?
};

export const clickUpgradeAllButton = () => {
  cy.get("[data-testid='upgradeAllButton']").click();
};
