import { appendRandomString, deleteEntity, submitButtonClick } from "commands/common";
import { createTestConnection } from "commands/connection";
import { deleteDestination } from "commands/destination";
import { deleteSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";
import {
  confirmStreamConfigurationChangedPopup,
  selectSchedule,
  fillOutDestinationPrefix,
  goToReplicationTab,
  setupDestinationNamespaceCustomFormat,
  selectFullAppendSyncMode,
  checkSuccessResult,
} from "pages/replicationPage";
import { openSourceDestinationFromGrid, goToSourcePage } from "pages/sourcePage";
import { goToSettingsPage } from "pages/settingsConnectionPage";

describe("Connection main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new connection", () => {
    const sourceName = appendRandomString("Test connection source cypress");
    const destName = appendRandomString("Test connection destination cypress")

    createTestConnection(sourceName, destName);

    cy.get("div").contains(sourceName).should("exist");
    cy.get("div").contains(destName).should("exist");

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Update connection", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    const sourceName = appendRandomString("Test update connection source cypress");
    const destName = appendRandomString("Test update connection destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    selectSchedule("Every hour");
    fillOutDestinationPrefix("auto_test");

    submitButtonClick();

    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
    });

    checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Update connection (pokeAPI)", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress")

    createTestConnection(
      sourceName,
      destName
    );

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid("Test update connection Local JSON destination cypress");

    goToReplicationTab();

    selectSchedule("Every hour");
    fillOutDestinationPrefix("auto_test");
    setupDestinationNamespaceCustomFormat("_test");
    selectFullAppendSyncMode();

    submitButtonClick();
    confirmStreamConfigurationChangedPopup();

    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
      expect(interception.request.method).to.eq("POST");
      expect(interception.request).property("body").to.contain({
        name: sourceName + " <> " + destName + "Connection name",
        prefix: "auto_test",
        namespaceDefinition: "customformat",
        namespaceFormat: "${SOURCE_NAMESPACE}_test",
        status: "active",
      });
      expect(interception.request.body.scheduleData.basicSchedule).to.contain({
        units: 1,
        timeUnit: "hours",
      });

      const streamToUpdate = interception.request.body.syncCatalog.streams[0];

      expect(streamToUpdate.config).to.contain({
        aliasName: "pokemon",
        destinationSyncMode: "append",
        selected: true,
      });

      expect(streamToUpdate.stream).to.contain({
        name: "pokemon",
      });
      expect(streamToUpdate.stream.supportedSyncModes).to.contain("full_refresh");
    });
    checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Delete connection", () => {
    const sourceName = "Test delete connection source cypress";
    const destName = "Test delete connection destination cypress";
    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToSettingsPage();

    deleteEntity();

    deleteSource(sourceName);
    deleteDestination(destName);
  });
});
