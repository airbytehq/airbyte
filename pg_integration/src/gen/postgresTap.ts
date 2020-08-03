/**
 * sync configurations needed to configure a postgres tap
 */
export interface PostgresTap {
  /**
   * all configuration information needed for creating a connection.
   */
  postgresConnectionConfiguration?: PostgresConnectionConfiguration;
  /**
   * postgres specific configuration for sync step
   */
  postgresSyncConfiguration?: PostgresSyncConfiguration;
  /**
   * describes the result of a 'test connection' action.
   */
  standardConnectionStatus?: StandardConnectionStatus;
  /**
   * describes the standard output for any discovery run.
   */
  standardDiscoveryOutput?: StandardDiscoveryOutput;
  /**
   * configuration required for sync for ALL taps
   */
  standardSyncConfiguration?: StandardSyncConfiguration;
  /**
   * standard information output by ALL taps for a sync step (our version of state.json)
   */
  standardSyncOutput?: StandardSyncOutput;
}

/**
 * all configuration information needed for creating a connection.
 */
export interface PostgresConnectionConfiguration {
  database?: string;
  host:      string;
  password?: string;
  port:      number;
  user:      string;
}

/**
 * postgres specific configuration for sync step
 */
export interface PostgresSyncConfiguration {
  tables: PostgresSyncConfigurationTable[];
}

export interface PostgresSyncConfigurationTable {
  columns: PurpleColumn[];
  name:    string;
}

export interface PurpleColumn {
  name: string;
}

/**
 * describes the result of a 'test connection' action.
 */
export interface StandardConnectionStatus {
  message?: string;
  status:   StandardConnectionStatusStatus;
}

export enum StandardConnectionStatusStatus {
  Failure = "failure",
  Success = "success",
}

/**
 * describes the standard output for any discovery run.
 */
export interface StandardDiscoveryOutput {
  schema: Schema;
}

/**
 * describes the available schema.
 */
export interface Schema {
  tables?: SchemaTable[];
}

export interface SchemaTable {
  columns: FluffyColumn[];
  name:    string;
}

export interface FluffyColumn {
  dataType: DataType;
  name:     string;
}

export enum DataType {
  Boolean = "boolean",
  Number = "number",
  String = "string",
  UUID = "uuid",
}

/**
 * configuration required for sync for ALL taps
 */
export interface StandardSyncConfiguration {
  syncMode?: SyncMode;
}

export enum SyncMode {
  Append = "append",
  FullRefresh = "full_refresh",
}

/**
 * standard information output by ALL taps for a sync step (our version of state.json)
 */
export interface StandardSyncOutput {
  recordsSynced?: number;
  status?:        StandardSyncOutputStatus;
  version?:       number;
}

export enum StandardSyncOutputStatus {
  Cancelled = "cancelled",
  Completed = "completed",
  Failed = "failed",
}
