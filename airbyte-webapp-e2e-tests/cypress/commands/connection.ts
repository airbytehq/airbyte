import { submitButtonClick } from "./common";
import { createTestDestination } from "./destination";
import { createPokeTestSource, createTestSource } from "./source";

export const createTestConnection = (sourceName: string, destinationName: string) => {
  cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
  cy.intercept("/api/v1/web_backend/connections/create").as("createConnection");

  switch (true) {
    case sourceName.includes('PokeAPI'):
      createPokeTestSource(sourceName)
      break;
    case sourceName.includes('Postgres'):
      createTestSource(sourceName);
      break;
    default:
      createTestSource(sourceName);
  }

  createTestDestination(destinationName);
  cy.wait(3000);

  cy.get("div[data-testid='select-source']").click();
  cy.get("div").contains(sourceName).click();

  cy.wait("@discoverSchema");

  cy.get("input[data-testid='connectionName']").type("Connection name");
  cy.get("div[data-testid='schedule']").click();
  cy.get("div[data-testid='Manual']").click();

  cy.get("div[data-testid='namespaceDefinition']").click();
  cy.get("div[data-testid='namespaceDefinition-source']").click();
  submitButtonClick();

  cy.wait("@createConnection");
};
