export interface Connection {
  connectionId: string;
  destination: Destination;
  destinationId: string;
  isSyncing: boolean;
  name: string;
  scheduleType: string;
  schemaChange: string;
  source: Source;
  sourceId: string;
  status: "active" | "inactive" | "deprecated";
  nonBreakingChangesPreference: "ignore" | "disable";
  syncCatalog: SyncCatalog;
}

export interface ConnectionCreateRequestBody {
  destinationId: string;
  geography: string;
  name: string;
  namespaceDefinition: string;
  namespaceFormat: string;
  nonBreakingChangesPreference: "ignore" | "disable";
  operations: unknown[];
  prefix: string;
  scheduleType: string;
  sourceCatalogId: string;
  sourceId: string;
  status: "active";
  syncCatalog: SyncCatalog;
}

export interface ConnectionGetBody {
  connectionId: string;
  withRefreshedCatalog?: boolean;
}

export interface ConnectionsList {
  connections: Connection[];
}

export interface Destination {
  name: string;
  destinationDefinitionId: string;
  destinationName: string;
  destinationId: string;
  connectionConfiguration: Record<string, unknown>;
}

export interface DestinationsList {
  destinations: Destination[];
}

export interface Source {
  name: string;
  sourceDefinitionId: string;
  sourceName: string;
  sourceId: string;
  connectionConfiguration: Record<string, unknown>;
}

export interface SourceDiscoverSchema {
  catalog: SyncCatalog;
  catalogId: string;
}

export interface SourcesList {
  sources: Source[];
}

export interface SyncCatalog {
  streams: SyncCatalogStream[];
}

export interface SyncCatalogStream {
  config: Record<string, unknown>;
  stream: Record<string, unknown>;
}
