import { clickOnCellInTable } from "commands/common";

const settingsTab = "div[data-id='settings-step']";
const sourceColumnName = "Source name";
const destinationColumnName = "Destination name";
const connectionsTable = "table[data-testid='connectionsTable']";

export const openConnectionOverviewBySourceName = (sourceName: string) => {
  clickOnCellInTable(connectionsTable, sourceColumnName, sourceName);
};

export const openConnectionOverviewByDestinationName = (destinationName: string) => {
  clickOnCellInTable(connectionsTable, destinationColumnName, destinationName);
};

export const goToSettingsPage = () => {
  cy.get(settingsTab).click();
};
