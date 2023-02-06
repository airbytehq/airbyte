type ConnectorType = "source" | "destination";
const existingConnectorDropdown = `div[data-testid='entityId']`;
const getExistingConnectorDropdownOption = (connectorName: string) => `div[data-testid='${connectorName}']`;
const useExistingConnectorButton = (connectorType: ConnectorType) =>
  `button[data-testid='use-existing-${connectorType}-button']`;

const pageHeaderContainer = `div[data-testid='page-header-container']`;
const newConnectionPageTitle = "New connection";

export const selectExistingConnectorFromDropdown = (connectorName: string) =>
  cy
    .get(existingConnectorDropdown)
    .click()
    .within(() => cy.get(getExistingConnectorDropdownOption(connectorName)).click());

export const clickUseExistingConnectorButton = (connectorType: ConnectorType) =>
  cy.get(useExistingConnectorButton(connectorType)).click();

export const isNewConnectionPageHeaderVisible = () =>
  cy.get(pageHeaderContainer).contains(newConnectionPageTitle).should("be.visible");

// Route checking
export const isAtNewConnectionPage = () => cy.url().should("include", `/connections/new-connection`);
export const isAtConnectionOverviewPage = (connectionId: string) =>
  cy.url().should("include", `connections/${connectionId}/status`);
