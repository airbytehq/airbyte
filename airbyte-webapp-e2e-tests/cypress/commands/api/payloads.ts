import { ConnectionCreateRequestBody } from "./types";
import { getWorkspaceId } from "./workspace";

type RequiredConnectionCreateRequestProps = "name" | "sourceId" | "destinationId" | "syncCatalog" | "sourceCatalogId";
type CreationConnectRequestParams = Pick<ConnectionCreateRequestBody, RequiredConnectionCreateRequestProps> &
  Partial<Omit<ConnectionCreateRequestBody, RequiredConnectionCreateRequestProps>>;

export const getConnectionCreateRequest = (params: CreationConnectRequestParams): ConnectionCreateRequestBody => ({
  geography: "auto",
  namespaceDefinition: "source",
  namespaceFormat: "${SOURCE_NAMESPACE}",
  nonBreakingChangesPreference: "ignore",
  operations: [],
  prefix: "",
  scheduleType: "manual",
  status: "active",
  ...params,
});

export const getPostgresCreateSourceBody = (name: string) => ({
  name,
  sourceDefinitionId: "decd338e-5647-4c0b-adf4-da0e75f5a750",
  workspaceId: getWorkspaceId(),
  connectionConfiguration: {
    ssl_mode: { mode: "disable" },
    tunnel_method: { tunnel_method: "NO_TUNNEL" },
    replication_method: { method: "Standard" },
    ssl: false,
    port: 5433,
    schemas: ["public"],
    host: "localhost",
    database: "airbyte_ci_source",
    username: "postgres",
    password: "secret_password",
  },
});

export const getE2ETestingCreateDestinationBody = (name: string) => ({
  name,
  workspaceId: getWorkspaceId(),
  destinationDefinitionId: "2eb65e87-983a-4fd7-b3e3-9d9dc6eb8537",
  connectionConfiguration: {
    type: "LOGGING",
    logging_config: {
      logging_type: "FirstN",
      max_entry_count: 100,
    },
  },
});

export const getPostgresCreateDestinationBody = (name: string) => ({
  name,
  workspaceId: getWorkspaceId(),
  destinationDefinitionId: "25c5221d-dce2-4163-ade9-739ef790f503",
  connectionConfiguration: {
    ssl_mode: { mode: "disable" },
    tunnel_method: { tunnel_method: "NO_TUNNEL" },
    ssl: false,
    port: 5434,
    schema: "public",
    host: "localhost",
    database: "airbyte_ci_destination",
    username: "postgres",
    password: "secret_password",
  },
});
