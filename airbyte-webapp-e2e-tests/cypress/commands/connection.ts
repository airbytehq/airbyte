import { submitButtonClick } from "./common";
import { createLocalJsonDestination, createPostgresDestination } from "./destination";
import { createPokeApiSource, createPostgresSource } from "./source";
import { openAddSource } from "pages/destinationPage";
import { selectSchedule, setupDestinationNamespaceSourceFormat, enterConnectionName } from "pages/replicationPage";

enum Schedule {
  MANUAL = "Manual",
}

interface ReplicationSettings {
  schedule: Schedule;
}

export const createTestConnection = (
  sourceName: string,
  destinationName: string,
  connectionSettings: ReplicationSettings = {} as ReplicationSettings
) => {
  cy.intercept("/api/v1/sources/discover_schema").as("discoverSchema");
  cy.intercept("/api/v1/web_backend/connections/create").as("createConnection");

  switch (true) {
    case sourceName.includes("PokeAPI"):
      createPokeApiSource(sourceName, "luxray");
      break;

    case sourceName.includes("Postgres"):
      createPostgresSource(sourceName);
      break;
    default:
      createPostgresSource(sourceName);
  }

  switch (true) {
    case destinationName.includes("Postgres"):
      createPostgresDestination(destinationName);
      break;
    case destinationName.includes("JSON"):
      createLocalJsonDestination(destinationName);
      break;
    default:
      createLocalJsonDestination(destinationName);
  }

  cy.wait(5000);

  openAddSource();
  cy.get("div").contains(sourceName).click();

  cy.wait("@discoverSchema");
  const { schedule } = connectionSettings;
  // enterConnectionName("Connection name"); // FIXME: do we need to append tha string to name?
  if (schedule) {
    selectSchedule(schedule);
  }
  // setupDestinationNamespaceSourceFormat(); // FIXME: do we need just to click on inputs?
  submitButtonClick();

  cy.wait("@createConnection", { requestTimeout: 10000 });
};
