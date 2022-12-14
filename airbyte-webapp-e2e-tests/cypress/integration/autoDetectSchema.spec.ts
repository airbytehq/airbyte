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
  requestSourceDiscoverSchema,
  requestWorkspaceId,
} from "commands/api";
import { Connection, Destination, Source } from "commands/api/types";
import { initialSetupCompleted } from "commands/workspaces";

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
  });

  it("creates a source", async () => {
    expect(connection.connectionId).to.be.a("string");
  });
});
