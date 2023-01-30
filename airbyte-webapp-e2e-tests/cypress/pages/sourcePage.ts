import { clickOnCellInTable } from "commands/common";

const newSource = "button[data-id='new-source']";
const sourcesTable = "table[data-testid='sourcesTable']";
const sourceNameColumn = "Name";

export const goToSourcePage = () => {
  cy.intercept("/api/v1/sources/list").as("getSourcesList");
  cy.visit("/source");
  cy.wait(3000);
};

export const openSourceDestinationFromGrid = (value: string) => {
  cy.get("div").contains(value).click();
};

export const openSourceOverview = (sourceName: string) => {
  clickOnCellInTable(sourcesTable, sourceNameColumn, sourceName);
};

export const openNewSourceForm = () => {
  cy.wait("@getSourcesList").then(({ response }) => {
    if (response?.body.sources.length) {
      cy.get(newSource).click();
    }
  });
  cy.url().should("include", `/source/new-source`);
};
