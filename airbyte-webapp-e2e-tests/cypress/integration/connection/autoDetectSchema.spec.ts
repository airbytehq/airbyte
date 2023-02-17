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
import * as connectionPage from "pages/connection/connectionPageObject";
import * as connectionListPage from "pages/connection/connectionListPageObject";
import * as catalogDiffModal from "pages/connection/catalogDiffModalPageObject";
import * as replicationPage from "pages/connection/connectionReplicationPageObject";
import streamsTablePageObject from "pages/connection/streamsTablePageObject";

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
      connectionListPage.visit();
      connectionListPage.getSchemaChangeIcon(connection, "non_breaking").should("exist");
      connectionListPage.getManualSyncButton(connection).should("be.enabled");
    });

    it("shows non-breaking change that can be saved after refresh", () => {
      // Need to continue running but async breaks everything
      connectionPage.visit(connection, "replication");

      replicationPage.checkSchemaChangesDetected({ breaking: false });
      replicationPage.clickSchemaChangesReviewButton();
      connectionPage.getSyncEnabledSwitch().should("be.enabled");

      catalogDiffModal.shouldExist();
      catalogDiffModal.clickCloseButton();

      replicationPage.checkSchemaChangesDetectedCleared();

      replicationPage.clickSaveButton();
      connectionPage.getSyncEnabledSwitch().should("be.enabled");
    });

    it("clears non-breaking change when db changes are restored", () => {
      connectionPage.visit(connection, "replication");

      replicationPage.checkSchemaChangesDetected({ breaking: false });

      runDbQuery(alterTable("public.users", { add: ["updated_at TIMESTAMP"] }));
      replicationPage.clickSchemaChangesReviewButton();

      replicationPage.checkSchemaChangesDetectedCleared();
      replicationPage.checkNoDiffToast();
    });
  });

  describe("breaking changes", () => {
    beforeEach(() => {
      const streamName = "users";
      connectionPage.visit(connection, "replication");

      // Change users sync mode
      streamsTablePageObject.searchStream(streamName);
      streamsTablePageObject.selectSyncMode("Incremental", "Deduped + history");
      streamsTablePageObject.selectCursorField(streamName, "updated_at");
      replicationPage.clickSaveButton();

      // Remove cursor from db and refreshs schema to force breaking change detection
      runDbQuery(alterTable("public.users", { drop: ["updated_at"] }));
      requestGetConnection({ connectionId: connection.connectionId, withRefreshedCatalog: true });
      cy.reload();
    });

    it("shows breaking change on list page", () => {
      connectionListPage.visit();
      connectionListPage.getSchemaChangeIcon(connection, "breaking").should("exist");
      connectionListPage.getManualSyncButton(connection).should("be.disabled");
    });

    it("shows breaking change that can be saved after refresh and fix", () => {
      connectionPage.visit(connection, "replication");

      // Confirm that breaking changes are there
      replicationPage.checkSchemaChangesDetected({ breaking: true });
      replicationPage.clickSchemaChangesReviewButton();
      connectionPage.getSyncEnabledSwitch().should("be.disabled");

      catalogDiffModal.shouldExist();
      catalogDiffModal.clickCloseButton();
      replicationPage.checkSchemaChangesDetectedCleared();

      // Fix the conflict
      streamsTablePageObject.searchStream("users");
      streamsTablePageObject.selectSyncMode("Full refresh", "Append");

      replicationPage.clickSaveButton();
      connectionPage.getSyncEnabledSwitch().should("be.enabled");
    });

    it("clears breaking change when db changes are restored", () => {
      connectionPage.visit(connection, "replication");

      replicationPage.checkSchemaChangesDetected({ breaking: true });

      runDbQuery(alterTable("public.users", { add: ["updated_at TIMESTAMP"] }));
      replicationPage.clickSchemaChangesReviewButton();

      replicationPage.checkSchemaChangesDetectedCleared();
      replicationPage.checkNoDiffToast();
    });
  });

  describe("non-breaking schema update preference", () => {
    it("saves non-breaking schema update preference change", () => {
      connectionPage.visit(connection, "replication");
      replicationPage.selectNonBreakingChangesPreference("disable");

      cy.intercept("/api/v1/web_backend/connections/update").as("updatesNonBreakingPreference");

      replicationPage.clickSaveButton({ confirm: false });

      cy.wait("@updatesNonBreakingPreference").then((interception) => {
        assert.equal((interception.response?.body as Connection).nonBreakingChangesPreference, "disable");
      });
    });
  });
});
