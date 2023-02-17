import { appendRandomString, deleteEntity, submitButtonClick } from "commands/common";
import { createTestConnection } from "commands/connection";
import { deleteDestination } from "commands/destination";
import { deleteSource } from "commands/source";
import { initialSetupCompleted } from "commands/workspaces";
import * as connectionForm from "pages/connection/connectionFormPageObject";
import { goToSourcePage, openSourceOverview } from "pages/sourcePage";
import * as connectionSettings from "pages/connection/connectionSettingsPageObject";
import { cleanDBSource, makeChangesInDBSource, populateDBSource } from "commands/db";
import * as catalogDiffModal from "pages/connection/catalogDiffModalPageObject";
import {
  interceptGetConnectionRequest,
  interceptUpdateConnectionRequest,
  waitForGetConnectionRequest,
  waitForUpdateConnectionRequest,
} from "commands/interceptors";
import { goToReplicationTab } from "pages/connection/connectionPageObject";
import * as replicationPage from "pages/connection/connectionReplicationPageObject";
import streamsTablePageObject from "pages/connection/streamsTablePageObject";

describe("Connection - creation, updating connection replication settings, deletion", () => {
  beforeEach(() => {
    initialSetupCompleted();

    interceptGetConnectionRequest();
    interceptUpdateConnectionRequest();
  });

  it("Create Postgres <> LocalJSON connection, check it's creation", () => {
    const sourceName = appendRandomString("Test connection source cypress");
    const destName = appendRandomString("Test connection destination cypress");

    createTestConnection(sourceName, destName);
    cy.get("div").contains(sourceName).should("exist");
    cy.get("div").contains(destName).should("exist");

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create Postgres <> LocalJSON connection, update connection replication settings - select schedule and add destination prefix", () => {
    const sourceName = appendRandomString("Test update connection source cypress");
    const destName = appendRandomString("Test update connection destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    connectionForm.selectSchedule("Every hour");
    connectionForm.fillOutDestinationPrefix("auto_test");

    submitButtonClick();

    waitForUpdateConnectionRequest().then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
    });

    replicationPage.checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it(`Creates PokeAPI <> Local JSON connection, update connection replication settings - 
  select schedule, add destination prefix, set destination namespace custom format, change prefix and make sure that it's applied to all streams`, () => {
    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    connectionForm.selectSchedule("Every hour");
    connectionForm.fillOutDestinationPrefix("auto_test");
    connectionForm.setupDestinationNamespaceCustomFormat("_test");
    streamsTablePageObject.selectSyncMode("Full refresh", "Append");

    const prefix = "auto_test";
    connectionForm.fillOutDestinationPrefix(prefix);

    // Ensures the prefix is applied to the streams
    assert(cy.get(`[title*="${prefix}"]`));

    submitButtonClick();
    replicationPage.confirmStreamConfigurationChangedPopup();

    waitForUpdateConnectionRequest().then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
      expect(interception.request.method).to.eq("POST");
      expect(interception.request)
        .property("body")
        .to.contain({
          name: `${sourceName} <> ${destName}Connection name`,
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
    replicationPage.checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create PokeAPI <> Local JSON connection, update connection replication settings - edit the schedule type one by one - cron, manual, every hour", () => {
    const sourceName = appendRandomString("Test connection source cypress PokeAPI");
    const destName = appendRandomString("Test connection destination cypress");

    createTestConnection(sourceName, destName);

    goToReplicationTab();

    connectionForm.selectSchedule("Cron");
    submitButtonClick();
    replicationPage.checkSuccessResult();

    connectionForm.selectSchedule("Manual");
    submitButtonClick();
    replicationPage.checkSuccessResult();

    connectionForm.selectSchedule("Every hour");
    submitButtonClick();
    replicationPage.checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create PokeAPI <> Local JSON connection, update connection replication settings - make sure that saving a connection's schedule type only changes expected values", () => {
    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    let loadedConnection: any = null; // Should be a WebBackendConnectionRead
    waitForGetConnectionRequest().then((interception) => {
      const {
        scheduleType: readScheduleType,
        scheduleData: readScheduleData,
        ...connectionRead
      } = interception.response?.body;
      loadedConnection = connectionRead;

      expect(loadedConnection).not.to.eq(null);
      expect(readScheduleType).to.eq("manual");
      expect(readScheduleData).to.eq(undefined);
    });

    goToReplicationTab();

    connectionForm.selectSchedule("Every hour");
    submitButtonClick();

    waitForUpdateConnectionRequest().then((interception) => {
      // Schedule is pulled out here, but we don't do anything with is as it's legacy
      const { scheduleType, scheduleData, schedule, ...connectionUpdate } = interception.response?.body;
      expect(scheduleType).to.eq("basic");
      expect(scheduleData.basicSchedule).to.deep.eq({
        timeUnit: "hours",
        units: 1,
      });

      expect(loadedConnection).to.deep.eq(connectionUpdate);
    });
    replicationPage.checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create PokeAPI <> Local JSON connection, and delete connection", () => {
    const sourceName = "Test delete connection source cypress";
    const destName = "Test delete connection destination cypress";
    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    connectionSettings.goToSettingsPage();

    deleteEntity();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create PokeAPI <> Local JSON connection, update connection replication settings - set destination namespace with 'Custom format' option", () => {
    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    const namespace = "_DestinationNamespaceCustomFormat";
    connectionForm.setupDestinationNamespaceCustomFormat(namespace);

    // Ensures the DestinationNamespace is applied to the streams
    assert(cy.get(`[title*="${namespace}"]`));

    submitButtonClick();

    waitForUpdateConnectionRequest().then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
      expect(interception.request.method).to.eq("POST");
      expect(interception.request)
        .property("body")
        .to.contain({
          name: `${sourceName} <> ${destName}Connection name`,
          namespaceDefinition: "customformat",
          namespaceFormat: "${SOURCE_NAMESPACE}_DestinationNamespaceCustomFormat",
          status: "active",
        });

      const streamToUpdate = interception.request.body.syncCatalog.streams[0];

      expect(streamToUpdate.stream).to.contain({
        name: "pokemon",
      });
    });
    replicationPage.checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create PokeAPI <> Local JSON connection, update connection replication settings - set destination namespace with 'Mirror source structure' option", () => {
    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    const namespace = "<source schema>";

    // Ensures the DestinationNamespace is applied to the streams
    assert(cy.get(`[title*="${namespace}"]`));

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create PokeAPI <> Local JSON connection, update connection replication settings - set destination namespace with 'Destination default' option", () => {
    const sourceName = appendRandomString("Test update connection PokeAPI source cypress");
    const destName = appendRandomString("Test update connection Local JSON destination cypress");

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    connectionForm.setupDestinationNamespaceDefaultFormat();

    const namespace = "<destination schema>";

    // Ensures the DestinationNamespace is applied to the streams
    assert(cy.get(`[title*="${namespace}"]`));

    submitButtonClick();

    waitForUpdateConnectionRequest().then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
      expect(interception.request.method).to.eq("POST");
      expect(interception.request)
        .property("body")
        .to.contain({
          name: `${sourceName} <> ${destName}Connection name`,
          namespaceDefinition: "destination",
          namespaceFormat: "${SOURCE_NAMESPACE}",
          status: "active",
        });

      const streamToUpdate = interception.request.body.syncCatalog.streams[0];

      expect(streamToUpdate.stream).to.contain({
        name: "pokemon",
      });
    });
    replicationPage.checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });
});

describe("Connection - stream details", () => {
  beforeEach(() => {
    initialSetupCompleted();
    populateDBSource();
  });

  afterEach(() => {
    cleanDBSource();
  });

  it("Create Postgres <> Postgres connection, connection replication settings, expand stream details", () => {
    const sourceName = appendRandomString("Test connection Postgres source cypress");
    const destName = appendRandomString("Test connection Postgres destination cypress");
    const streamName = "users";

    const collectionNames = ["email", "id", "name", "updated_at"];
    const collectionTypes = ["String", "Integer", "String", "Datetime"];

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    streamsTablePageObject.searchStream(streamName);
    streamsTablePageObject.expandStreamDetailsByName(streamName);
    streamsTablePageObject.checkStreamFields(collectionNames, collectionTypes);

    deleteSource(sourceName);
    deleteDestination(destName);
  });
});

describe("Connection sync modes", () => {
  beforeEach(() => {
    initialSetupCompleted();
    populateDBSource();

    interceptUpdateConnectionRequest();
  });

  afterEach(() => {
    cleanDBSource();
  });

  it("Create Postgres <> Postgres connection, update connection replication settings - select 'Incremental Append' sync mode, select required Cursor field, verify changes", () => {
    const sourceName = appendRandomString("Test connection Postgres source cypress");
    const destName = appendRandomString("Test connection Postgres destination cypress");
    const streamName = "users";

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    streamsTablePageObject.searchStream(streamName);
    streamsTablePageObject.selectSyncMode("Incremental", "Append");
    streamsTablePageObject.selectCursorField(streamName, "updated_at");

    submitButtonClick();
    replicationPage.confirmStreamConfigurationChangedPopup();

    waitForUpdateConnectionRequest().then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
    });

    replicationPage.checkSuccessResult();

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    streamsTablePageObject.searchStream("users");
    streamsTablePageObject.checkCursorField(streamName, "updated_at");

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create Postgres <> Postgres connection, update connection replication settings - select 'Incremental Deduped History'(PK is defined), select Cursor field, verify changes", () => {
    const sourceName = appendRandomString("Test connection Postgres source cypress");
    const destName = appendRandomString("Test connection Postgres destination cypress");
    const streamName = "users";

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    streamsTablePageObject.searchStream(streamName);
    streamsTablePageObject.selectSyncMode("Incremental", "Deduped + history");
    streamsTablePageObject.selectCursorField(streamName, "updated_at");
    streamsTablePageObject.checkPreFilledPrimaryKeyField(streamName, "id");

    submitButtonClick();
    replicationPage.confirmStreamConfigurationChangedPopup();

    waitForUpdateConnectionRequest().then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
    });

    replicationPage.checkSuccessResult();

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    streamsTablePageObject.searchStream(streamName);

    streamsTablePageObject.checkCursorField(streamName, "updated_at");
    streamsTablePageObject.checkPreFilledPrimaryKeyField(streamName, "id");

    deleteSource(sourceName);
    deleteDestination(destName);
  });

  it("Create Postgres <> Postgres connection, update connection replication settings - select 'Incremental Deduped History'(PK is NOT defined), select Cursor field, select PK, verify changes", () => {
    const sourceName = appendRandomString("Test connection Postgres source cypress");
    const destName = appendRandomString("Test connection Postgres destination cypress");
    const streamName = "cities";

    createTestConnection(sourceName, destName);

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    streamsTablePageObject.searchStream(streamName);
    streamsTablePageObject.selectSyncMode("Incremental", "Deduped + history");
    streamsTablePageObject.selectCursorField(streamName, "city");
    streamsTablePageObject.isPrimaryKeyNonExist(streamName);
    streamsTablePageObject.selectPrimaryKeyField(streamName, ["city_code"]);

    submitButtonClick();
    replicationPage.confirmStreamConfigurationChangedPopup();

    waitForUpdateConnectionRequest().then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
    });

    replicationPage.checkSuccessResult();

    goToSourcePage();
    openSourceOverview(sourceName);
    connectionSettings.openConnectionOverviewByDestinationName(destName);

    goToReplicationTab();

    streamsTablePageObject.searchStream(streamName);

    streamsTablePageObject.checkCursorField(streamName, "city");
    streamsTablePageObject.checkPrimaryKey(streamName, ["city_code"]);

    deleteSource(sourceName);
    deleteDestination(destName);
  });
});

describe("Connection - detect source schema changes in source", () => {
  beforeEach(() => {
    initialSetupCompleted();
    populateDBSource();

    interceptUpdateConnectionRequest();
  });

  afterEach(() => {
    cleanDBSource();
  });

  it("Create Postgres <> Local JSON connection, update data in source (async), refresh source schema, check diff modal, reset streams", () => {
    const sourceName = appendRandomString(
      "Test refresh source schema with changed data - connection Postgres source cypress"
    );
    const destName = appendRandomString(
      "Test refresh source schema with changed data - connection Local JSON destination cypress"
    );

    createTestConnection(sourceName, destName);
    cy.get("div").contains(sourceName).should("exist");
    cy.get("div").contains(destName).should("exist");

    makeChangesInDBSource();
    goToReplicationTab();
    streamsTablePageObject.refreshSourceSchemaBtnClick();

    catalogDiffModal.shouldExist();

    cy.get(catalogDiffModal.removedStreamsTable).should("contain", "users");

    cy.get(catalogDiffModal.newStreamsTable).should("contain", "cars");

    catalogDiffModal.toggleStreamWithChangesAccordion("cities");
    cy.get(catalogDiffModal.removedFieldsTable).should("contain", "city_code");
    cy.get(catalogDiffModal.newFieldsTable).children().should("contain", "country").and("contain", "state");

    catalogDiffModal.clickCloseButton();

    streamsTablePageObject.toggleStreamEnabledState("cars");

    submitButtonClick();
    replicationPage.resetModalSaveBtnClick();

    waitForUpdateConnectionRequest().then((interception) => {
      assert.isNotNull(interception.response?.statusCode, "200");
    });

    replicationPage.checkSuccessResult();

    deleteSource(sourceName);
    deleteDestination(destName);
  });
});
