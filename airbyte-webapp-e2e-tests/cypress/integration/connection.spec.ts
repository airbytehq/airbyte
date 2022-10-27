import { appendRandomString, deleteEntity, submitButtonClick } from "commands/common";
import { createTestConnection } from "commands/connection";
import { deleteDestination } from "commands/destination";
import { deleteSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";
import { setupDestinationNamespaceDefaultFormat, confirmStreamConfigurationChangedPopup, selectSchedule, fillOutDestinationPrefix, goToReplicationTab, setupDestinationNamespaceCustomFormat, selectSyncMode, checkSuccessResult, searchStream, selectCursorField, checkCursorField, setupDestinationNamespaceSourceFormat} from "pages/replicationPage";
import { openSourceDestinationFromGrid, goToSourcePage } from "pages/sourcePage";
import { goToSettingsPage } from "pages/settingsConnectionPage";
import { update, ceil } from "cypress/types/lodash";

describe("Connection main actions", () => {
  beforeEach(() => {
    initialSetupCompleted();
  });

  it("Create new connection", () => {
    const sourceName = appendRandomString("Test connection source cypress");
    const destName = appendRandomString("Test connection destination cypress");

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

  it("Connection sync mode Incremental Append", () => {
    const sourceName = appendRandomString("Test connection Postgres source cypress");
    const destName = appendRandomString("Test connection Postgres destination cypress");

    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    searchStream("admins");
    selectSyncMode("Incremental", "Append");
    selectCursorField("email");

    submitButtonClick();
    confirmStreamConfigurationChangedPopup();

    cy.wait("@updateConnection", { timeout: 5000 }).then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
    });

    checkSuccessResult();

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    searchStream("admins");

    checkCursorField("email");

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Connection sync mode Incremental Deduped History", () => {
    const sourceName = appendRandomString("Test connection Postgres source cypress");
    const destName = appendRandomString("Test connection Postgres destination cypress");

    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    searchStream("admins");
    selectSyncMode("Incremental", "Deduped + history");
    selectCursorField("email");

    submitButtonClick();
    confirmStreamConfigurationChangedPopup();

    cy.wait(5000);

    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
    });

    checkSuccessResult();

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    searchStream("admins");

    checkCursorField("email");

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Update connection (pokeAPI)", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    selectSchedule("Every hour");
    fillOutDestinationPrefix("auto_test");
    setupDestinationNamespaceCustomFormat("_test");
    selectSyncMode("Full refresh", "Append");

    const prefix = "auto_test";
    fillOutDestinationPrefix(prefix);

    // Ensures the prefix is applied to the streams
    assert(cy.get(`[title*="${prefix}"]`));

    submitButtonClick();
    confirmStreamConfigurationChangedPopup();

    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
      expect(interception.request.method).to.eq("POST");
      expect(interception.request)
        .property("body")
        .to.contain({
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

  it("creates a connection, then edits the schedule type", () => {
    const sourceName = appendRandomString("Test connection source cypress PokeAPI");
    const destName = appendRandomString("Test connection destination cypress");

    createTestConnection(sourceName, destName);

    cy.get("div").contains(sourceName).should("exist");
    cy.get("div").contains(destName).should("exist");

    openSourceDestinationFromGrid(sourceName);

    goToReplicationTab();

    selectSchedule("Cron");
    submitButtonClick();
    checkSuccessResult();

    selectSchedule("Manual");
    submitButtonClick();
    checkSuccessResult();

    selectSchedule("Every hour");
    submitButtonClick();
    checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Saving a connection's schedule type only changes expected values", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");
    cy.intercept("/api/v1/web_backend/connections/get").as("getConnection");

    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(`${sourceName} <> ${destName}`);

    let loadedConnection: any = null; // Should be a WebBackendConnectionRead
    cy.wait("@getConnection").then((interception) => {
      const { scheduleType: readScheduleType, scheduleData: readScheduleData, ...connectionRead } = interception.response?.body;
      loadedConnection = connectionRead;

      expect(loadedConnection).not.to.eq(null);
      expect(readScheduleType).to.eq("manual");
      expect(readScheduleData).to.eq(undefined);
    });

    goToReplicationTab();

    selectSchedule("Every hour");
    submitButtonClick();

    cy.wait("@updateConnection").then((interception) => {
      // Schedule is pulled out here, but we don't do anything with is as it's legacy
      const { scheduleType, scheduleData, schedule, ...connectionUpdate } = interception.response?.body;
      expect(scheduleType).to.eq("basic");
      expect(scheduleData.basicSchedule).to.deep.eq({
        timeUnit: "hours",
        units: 1,
      });

      expect(loadedConnection).to.deep.eq(connectionUpdate);
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

  it("Saving a connection's destination namespace with 'Custom format' option", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    
    const namespace = "_DestinationNamespaceCustomFormat";
    setupDestinationNamespaceCustomFormat(namespace);

    // Ensures the DestinationNamespace is applied to the streams
    assert(cy.get(`[title*="${namespace}"]`));

    submitButtonClick();

    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
      expect(interception.request.method).to.eq("POST");
      expect(interception.request)
        .property("body")
        .to.contain({
          name: sourceName + " <> " + destName + "Connection name",
          namespaceDefinition: "customformat",
          namespaceFormat: "${SOURCE_NAMESPACE}_DestinationNamespaceCustomFormat",
          status: "active",
        });

      const streamToUpdate = interception.request.body.syncCatalog.streams[0];

      expect(streamToUpdate.stream).to.contain({
        name: "pokemon",
      });
    });
    checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Saving a connection's destination namespace with 'Mirror source structure' option", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    const namespace = "<source schema>";

    // Ensures the DestinationNamespace is applied to the streams
    assert(cy.get(`[title*="${namespace}"]`));

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Saving a connection's destination namespace with 'Destination default' option", () => {
    cy.intercept("/api/v1/web_backend/connections/update").as("updateConnection");

    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceDestinationFromGrid(sourceName);
    openSourceDestinationFromGrid(destName);

    goToReplicationTab();

    setupDestinationNamespaceDefaultFormat();

    const namespace = "<destination schema>";

    // Ensures the DestinationNamespace is applied to the streams
    assert(cy.get(`[title*="${namespace}"]`));

    submitButtonClick();

    cy.wait("@updateConnection").then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
      expect(interception.request.method).to.eq("POST");
      expect(interception.request)
        .property("body")
        .to.contain({
          name: sourceName + " <> " + destName + "Connection name",
          namespaceDefinition: "destination",
          namespaceFormat: "${SOURCE_NAMESPACE}",
          status: "active",
        });

      const streamToUpdate = interception.request.body.syncCatalog.streams[0];

      expect(streamToUpdate.stream).to.contain({
        name: "pokemon",
      });
    });
    checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });
});
