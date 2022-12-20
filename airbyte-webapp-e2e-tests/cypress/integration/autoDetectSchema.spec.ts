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
import { runDbQuery } from "commands/db/db";
import { alterTable, createUsersTableQuery, dropUsersTableQuery } from "commands/db/queries";
import { initialSetupCompleted } from "commands/workspaces";
import { getSyncEnabledSwitch, visitConnectionPage } from "pages/connectionPage";
import { checkCatalogDiffModal, clickCatalogDiffCloseButton } from "pages/modals/catalogDiffModal";
import {
  checkSchemaChangesDetected,
  checkSchemaChangesDetectedCleared,
  clickSaveReplication,
  clickSchemaChangesReviewButton,
  searchStream,
  selectCursorField,
  selectSyncMode,
} from "pages/replicationPage";

describe("Auto-detect schema changes", () => {
  let source: Source;
  let destination: Destination;
  let connection: Connection;

  beforeEach(async () => {
    initialSetupCompleted();
    await requestWorkspaceId();

    const sourceRequestBody = getPostgresCreateSourceBody("Auto-detect schema Source");
    const destinationRequestBody = getPostgresCreateDestinationBody("Auto-detect schema Destination");

    source = await requestCreateSource(sourceRequestBody);
    destination = await requestCreateDestination(destinationRequestBody);

    runDbQuery(dropUsersTableQuery);
    runDbQuery(createUsersTableQuery);

    const { catalog, catalogId } = await requestSourceDiscoverSchema(source.sourceId);

    const connectionRequestBody = await getConnectionCreateRequest({
      name: "Auto-detect schema test connection",
      sourceId: source.sourceId,
      destinationId: destination.destinationId,
      syncCatalog: catalog,
      sourceCatalogId: catalogId,
    });

    connection = await requestCreateConnection(connectionRequestBody);
  });

  afterEach(async () => {
    if (connection) {
      await requestDeleteConnection(connection.connectionId);
    }
    if (source) {
      await requestDeleteSource(source.sourceId);
    }
    if (destination) {
      await requestDeleteDestination(destination.destinationId);
    }

    runDbQuery(dropUsersTableQuery);
  });

  it("shows non-breaking change that can be saved after refresh", () => {
    runDbQuery(alterTable("public.users", { drop: ["updated_at"] }));
    requestGetConnection({ connectionId: connection.connectionId, withRefreshedCatalog: true });

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

  it("shows breaking change that can be saved after refresh and fix", () => {
    visitConnectionPage(connection, "replication");

    // Change users sync mode
    searchStream("users");
    selectSyncMode("Incremental", "Deduped + history");
    selectCursorField("updated_at");
    clickSaveReplication();

    // Remove cursor from db and refreshs schema to force breaking change detection
    runDbQuery(alterTable("public.users", { drop: ["updated_at"] }));
    requestGetConnection({ connectionId: connection.connectionId, withRefreshedCatalog: true }).then(console.log);

    // Reload the page to pick up the changes
    cy.reload();

    // Confirm that breaking changes are there
    checkSchemaChangesDetected({ breaking: true });
    clickSchemaChangesReviewButton();
    getSyncEnabledSwitch().should("be.disabled");

    checkCatalogDiffModal();
    clickCatalogDiffCloseButton();
    checkSchemaChangesDetectedCleared();

    // Fix the conflict
    searchStream("Users");
    selectSyncMode("Full refresh", "Append");

    clickSaveReplication();
    getSyncEnabledSwitch().should("be.enabled");
  });
});
