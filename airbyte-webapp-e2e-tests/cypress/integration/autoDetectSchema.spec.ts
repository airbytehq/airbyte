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
import { submitButtonClick } from "commands/common";
import { runDbQuery } from "commands/db/db";
import { alterTable, createUsersTableQuery, dropUsersTableQuery } from "commands/db/queries";
import { initialSetupCompleted } from "commands/workspaces";
import { visitConnectionPage } from "pages/connectionPage";
import { checkCatalogDiffModal, clickCatalogDiffCloseButton } from "pages/modals/catalogDiffModal";
import { checkSchemaChangesDetected, checkSchemaChangesDetectedCleared, checkSuccessResult, clickSaveReplication, clickSchemaChangesReviewButton } from "pages/replicationPage";

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

  it("has working non-breaking changes flow", () => {
    runDbQuery(alterTable("public.users", { drop: ['updated_at'] }))
    requestGetConnection({ connectionId: connection.connectionId, withRefreshedCatalog: true })

    // Need to continue running but async breaks everything
    visitConnectionPage(connection, 'replication');

    checkSchemaChangesDetected();
    clickSchemaChangesReviewButton();

    checkCatalogDiffModal();
    clickCatalogDiffCloseButton();

    checkSchemaChangesDetectedCleared();

    clickSaveReplication();
  });
});
