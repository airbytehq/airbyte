import { submitButtonClick } from "./common";
import { createLocalJsonDestination } from "./destination";
import { createPokeTestSource, createPostgresSource } from "./source";
import { openAddSource } from "pages/destinationPage"
import { selectSchedule, setupDestinationNamespaceSourceFormat, enterConnectionName } from "pages/replicationPage"

export const createTestConnection = (sourceName: string, destinationName: string) => {
  cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
  cy.intercept("/api/v1/web_backend/connections/create").as("createConnection");

  switch (true) {
    case sourceName.includes('PokeAPI'):
      createPokeTestSource(sourceName, "luxray")
      break;
    case sourceName.includes('Postgres'):
      createPostgresSource(sourceName, "localhost", "{selectAll}{del}5433", "airbyte_ci", "postgres", "secret_password");
      break;
    default:
      createPostgresSource(sourceName, "localhost", "{selectAll}{del}5433", "airbyte_ci", "postgres", "secret_password");
  }

  createLocalJsonDestination(destinationName, "/local");
  cy.wait(6000);

  openAddSource();
  cy.get("div").contains(sourceName).click();

  cy.wait("@discoverSchema");

  enterConnectionName("Connection name");
  selectSchedule("Manual");

  setupDestinationNamespaceSourceFormat();
  submitButtonClick();

  cy.wait("@createConnection");
};
