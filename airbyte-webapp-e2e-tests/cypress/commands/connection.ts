import { submitButtonClick } from "./common";
import { createLocalJsonDestination, createPostgresDestination } from "./destination";
import { createPokeApiSource, createPostgresSource } from "./source";
import { openAddSource } from "pages/destinationPage";
import { selectSchedule, setupDestinationNamespaceSourceFormat, enterConnectionName } from "pages/replicationPage";

export const createTestConnection = (sourceName: string, destinationName: string) => {
  cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
  cy.intercept("/api/v1/web_backend/connections/create").as("createConnection");

  switch (true) {
    case sourceName.includes("PokeAPI"):
      createPokeApiSource(sourceName, "luxray");
      break;

    case sourceName.includes('Postgres'):
      createPostgresSource(sourceName, "ec2-3-229-11-55.compute-1.amazonaws.com", "{selectAll}{del}5432", "d5pcodgtmh9pob", "yuxothkqynerju", "1c1771f795985693bc4f780130d7e8af895a3d48155007b93d21218e4bc07cd9", "demo");
      break;
    default:
      createPostgresSource(sourceName);
  }

  switch (true) {
    case destinationName.includes('Postgres'):
      createPostgresDestination(destinationName)
      break;
    case destinationName.includes('JSON'):
      createLocalJsonDestination(destinationName);
      break;
    default:
      createLocalJsonDestination(destinationName);
  }
  
  cy.wait(5000);

  openAddSource();
  cy.get("div").contains(sourceName).click();

  cy.wait("@discoverSchema");

  enterConnectionName("Connection name");
  selectSchedule("Manual");

  setupDestinationNamespaceSourceFormat();
  submitButtonClick();

  cy.wait(5000);
  cy.wait("@createConnection");
};
