import { WebBackendConnectionRead, WebBackendConnectionUpdate } from "core/request/AirbyteClient";

export const toWebBackendConnectionUpdate = (connection: WebBackendConnectionRead): WebBackendConnectionUpdate => ({
  name: connection.name,
  connectionId: connection.connectionId,
  namespaceDefinition: connection.namespaceDefinition,
  namespaceFormat: connection.namespaceFormat,
  prefix: connection.prefix,
  syncCatalog: connection.syncCatalog,
  scheduleData: connection.scheduleData,
  scheduleType: connection.scheduleType,
  status: connection.status,
  resourceRequirements: connection.resourceRequirements,
  operations: connection.operations,
  sourceCatalogId: connection.catalogId,
});

export const buildConnectionUpdate = (
  connection: WebBackendConnectionRead,
  connectionUpdate: Partial<WebBackendConnectionUpdate>
): WebBackendConnectionUpdate => ({
  skipReset: true,
  ...toWebBackendConnectionUpdate(connection),
  ...connectionUpdate,
});
