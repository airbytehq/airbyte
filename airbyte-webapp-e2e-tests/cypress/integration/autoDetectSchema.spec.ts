import {
  getConnectionCreateRequest,
  getPostgresCreateDestinationBody,
  getPostgresCreateSourceBody,
  requestCreateConnection,
  requestCreateDestination,
  requestCreateSource,
  requestDeleteConnection,
  requestDeleteDestination,
  requestDeleteSource,
  requestGetConnection,
  requestSourceDiscoverSchema,
  requestWorkspaceId,
} from "commands/api";
import { Connection, Destination, Source } from "commands/api/types";
import { appendRandomString } from "commands/common";
import { runDbQuery } from "commands/db/db";
import { alterTable, createUsersTableQuery, dropUsersTableQuery } from "commands/db/queries";
import { initialSetupCompleted } from "commands/workspaces";
import { getSyncEnabledSwitch, visitConnectionPage } from "pages/connectionPage";
import { getManualSyncButton, getSchemaChangeIcon, visitConnectionsListPage } from "pages/connnectionsListPage";
import { checkCatalogDiffModal, clickCatalogDiffCloseButton } from "pages/modals/catalogDiffModal";
import {
  checkSchemaChangesDetected,
  checkSchemaChangesDetectedCleared,
  clickSaveReplication,
  clickSchemaChangesReviewButton,
  searchStream,
  selectCursorField,
  selectNonBreakingChangesPreference,
  selectSyncMode,
} from "pages/replicationPage";

describe("Connection - Auto-detect schema changes", () => {
  let source: Source;
  let destination: Destination;
  let connection: Connection;

  beforeEach(() => {
    initialSetupCompleted();
    runDbQuery(dropUsersTableQuery);
    runDbQuery(createUsersTableQuery);

    requestWorkspaceId().then(() => {
      const sourceRequestBody = getPostgresCreateSourceBody(appendRandomString("Auto-detect schema Source"));
      const destinationRequestBody = getPostgresCreateDestinationBody(
        appendRandomString("Auto-detect schema Destination")
      );

      requestCreateSource(sourceRequestBody).then((sourceResponse) => {
        source = sourceResponse;
        requestCreateDestination(destinationRequestBody).then((destinationResponse) => {
          destination = destinationResponse;
        });

        requestSourceDiscoverSchema(source.sourceId).then(({ catalog, catalogId }) => {
          const connectionRequestBody = getConnectionCreateRequest({
            name: appendRandomString("Auto-detect schema test connection"),
            sourceId: source.sourceId,
            destinationId: destination.destinationId,
            syncCatalog: catalog,
            sourceCatalogId: catalogId,
          });
          requestCreateConnection(connectionRequestBody).then((connectionResponse) => {
            connection = connectionResponse;
          });
        });
      });
    });
  });

  afterEach(() => {
    if (connection) {
      requestDeleteConnection(connection.connectionId);
    }
    if (source) {
      requestDeleteSource(source.sourceId);
    }
    if (destination) {
      requestDeleteDestination(destination.destinationId);
    }

    runDbQuery(dropUsersTableQuery);
  });

  describe("non-breaking changes", () => {
    beforeEach(() => {
      runDbQuery(alterTable("public.users", { drop: ["updated_at"] }));
      requestGetConnection({ connectionId: connection.connectionId, withRefreshedCatalog: true });
    });

    it("shows non-breaking change on list page", () => {
      visitConnectionsListPage();
      getSchemaChangeIcon(connection, "non_breaking").should("exist");
      getManualSyncButton(connection).should("be.enabled");
    });

    it("shows non-breaking change that can be saved after refresh", () => {
      // Need to continue running but async breaks everything
      visitConnectionPage(connection, "replication");

      checkSchemaChangesDetected({ breaking: false });
      clickSchemaChangesReviewButton();
      getSyncEnabledSwitch().should("be.enabled");

      checkCatalogDiffModal();
      clickCatalogDiffCloseButton();

      checkSchemaChangesDetectedCleared();

      clickSaveReplication();
      getSyncEnabledSwitch().should("be.enabled");
    });
  });

  describe("breaking changes", () => {
    beforeEach(() => {
      const streamName = "users";
      visitConnectionPage(connection, "replication");

      // Change users sync mode
      searchStream(streamName);
      selectSyncMode("Incremental", "Deduped + history");
      selectCursorField(streamName, "updated_at");
      clickSaveReplication();

      // Remove cursor from db and refreshs schema to force breaking change detection
      runDbQuery(alterTable("public.users", { drop: ["updated_at"] }));
      requestGetConnection({ connectionId: connection.connectionId, withRefreshedCatalog: true });
      cy.reload();
    });

    it("shows breaking change on list page", () => {
      visitConnectionsListPage();
      getSchemaChangeIcon(connection, "breaking").should("exist");
      getManualSyncButton(connection).should("be.disabled");
    });

    it("shows breaking change that can be saved after refresh and fix", () => {
      visitConnectionPage(connection, "replication");

      // Confirm that breaking changes are there
      checkSchemaChangesDetected({ breaking: true });
      clickSchemaChangesReviewButton();
      getSyncEnabledSwitch().should("be.disabled");

      checkCatalogDiffModal();
      clickCatalogDiffCloseButton();
      checkSchemaChangesDetectedCleared();

      // Fix the conflict
      searchStream("users");
      selectSyncMode("Full refresh", "Append");

      clickSaveReplication();
      getSyncEnabledSwitch().should("be.enabled");
    });
  });

  describe("non-breaking schema update preference", () => {
    it("saves non-breaking schema update preference change", () => {
      visitConnectionPage(connection, "replication");
      selectNonBreakingChangesPreference("disable");

      cy.intercept("/api/v1/web_backend/connections/update").as("updatesNonBreakingPreference");

      clickSaveReplication({ confirm: false });

      cy.wait("@updatesNonBreakingPreference").then((interception) => {
        assert.equal((interception.response?.body as Connection).nonBreakingChangesPreference, "disable");
      });
    });
  });
});
