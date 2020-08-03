import {
  DataType,
  PostgresConnectionConfiguration,
  PostgresSyncConfiguration,
  StandardConnectionStatus,
  StandardConnectionStatusStatus,
  StandardDiscoveryOutput,
  StandardSyncConfiguration,
  StandardSyncOutput,
  StandardSyncOutputStatus
} from "./gen/postgresTap";

// interface that must be implemented for each tap.
interface ConduitTap<ConnectionConfiguration, SyncConfiguration, State> {
  // test connection
  testConnection(
    connectionConfiguration: ConnectionConfiguration
  ): StandardConnectionStatus;

  // discover
  discover(
    connectionConfiguration: ConnectionConfiguration
  ): StandardDiscoveryOutput;

  // sync
  sync(
    connectionConfiguration: ConnectionConfiguration,
    syncConfiguration: SyncConfiguration,
    standardSyncConfiguration: StandardSyncConfiguration,
    state: State
  ): [StandardSyncOutput, State];
}

const postgresConduitTapImplementation: ConduitTap<
  PostgresConnectionConfiguration,
  PostgresSyncConfiguration,
  any
> = {
  testConnection(
    connectionConfiguration: PostgresConnectionConfiguration
  ): StandardConnectionStatus {
    // attempts to connect to postgres using connection configuration.
    return { status: StandardConnectionStatusStatus.Success };
  },

  discover(
    connectionConfiguration: PostgresConnectionConfiguration
  ): StandardDiscoveryOutput {
    // attempts to read the schema using connection configuration.
    return {
      schema: {
        tables: [
          {
            name: "users",
            columns: [
              {
                name: "id",
                dataType: DataType.UUID
              },
              {
                name: "username",
                dataType: DataType.String
              }
            ]
          }
        ]
      }
    };
  },
  sync(
    connectionConfiguration: PostgresConnectionConfiguration,
    syncConfiguration: PostgresSyncConfiguration,
    standardSyncConfiguration: StandardSyncConfiguration,
    state: any
  ): [StandardSyncOutput, any] {
    // 1. runs singer discovery. obtains a catalog.json
    // 2. uses contents of PostgresSyncConfiguration and standardSyncConfiguration to mutate the catalog.json so that the
    // desired sync type is used and only the desired tables / columns are synced.
    //   i. specifically in this case this requires taking the `syncMode` field from `standardSyncConfiguration` and
    //   injecting it into the `replication-method` of each stream in he catalog json.
    //   ii. in catalog.json removing any stream (table) or columns that are are not explicitly mentioned in
    //   `PostgresSyncConfiguration`. validating that all tables / columns that are mentioned actually exist in the
    //   catalog.
    // 3. runs singer sync
    // 4. outputs status of the run. also outputs the state file that singer producers. this is just stored as a blob.
    return [
      {
        status: StandardSyncOutputStatus.Completed,
        recordsSynced: 10,
        version: 1596437234
      },
      {
        _comment: "whatever garbage is in state.json"
      }
    ];
  }
};

export { ConduitTap, postgresConduitTapImplementation };
