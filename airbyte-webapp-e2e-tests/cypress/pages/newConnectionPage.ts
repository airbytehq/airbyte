type ConnectorType = "source" | "destination";
const existingConnectorDropdown = `div[data-testid='entityId']`;
const getExistingConnectorDropdownOption = (connectorName: string) => `div[data-testid='${connectorName}']`;
const useExistingConnectorButton = (connectorType: ConnectorType) =>
  `button[data-testid='use-existing-${connectorType}-button']`;

const pageHeaderContainer = `div[data-testid='page-header-container']`;
const newConnectionPageTitle = "New connection";

const connectorHeaderGroupIcon = (connectorType: ConnectorType) =>
  `span[data-testid='connector-header-group-icon-container-${connectorType}']`;
const catalogTreeTableHeader = `div[data-testid='catalog-tree-table-header']`;
const catalogTreeTableBody = `div[data-testid='catalog-tree-table-body']`;

export const selectExistingConnectorFromDropdown = (connectorName: string) =>
  cy
    .get(existingConnectorDropdown)
    .click()
    .within(() => cy.get(getExistingConnectorDropdownOption(connectorName)).click());

export const clickUseExistingConnectorButton = (connectorType: ConnectorType) =>
  cy.get(useExistingConnectorButton(connectorType)).click();

export const isNewConnectionPageHeaderVisible = () =>
  cy.get(pageHeaderContainer).contains(newConnectionPageTitle).should("be.visible");

/*
 Route checking
 */
export const isAtNewConnectionPage = () => cy.url().should("include", `/connections/new-connection`);
export const isAtConnectionOverviewPage = (connectionId: string) =>
  cy.url().should("include", `connections/${connectionId}/status`);

/*
  Stream table
 */
export const checkConnectorIconAndTitle = (connectorType: ConnectorType) => {
  const connectorIcon = connectorHeaderGroupIcon(connectorType);
  cy.get(connectorIcon)
    .contains(connectorType, { matchCase: false })
    .within(() => {
      cy.get("img").should("have.attr", "src").should("not.be.empty");
    });
};

export const checkColumnNames = () => {
  const columnNames = ["Sync", "Namespace", "Stream name", "Sync mode", "Cursor field", "Primary key"];
  cy.get(catalogTreeTableHeader).within(($header) => {
    columnNames.forEach((columnName) => {
      cy.contains(columnName);
    });
    // we have two Namespace columns
    cy.get(`div:contains(${columnNames[1]})`).should("have.length", 2);
    // we have two Stream Name columns
    cy.get(`div:contains(${columnNames[2]})`).should("have.length", 2);
  });
};

export const checkAmountOfStreamTableRows = (expectedAmountOfRows: number) =>
  cy
    .get(catalogTreeTableBody)
    .find("[data-testid^='catalog-tree-table-row-']")
    .should("have.length", expectedAmountOfRows);

export const scrollTableToStream = (streamName: string) => {
  cy.get(catalogTreeTableBody).contains(streamName).scrollIntoView();
};

export const isStreamTableRowVisible = (streamName: string) =>
  cy.get(catalogTreeTableBody).contains(streamName).should("be.visible");
