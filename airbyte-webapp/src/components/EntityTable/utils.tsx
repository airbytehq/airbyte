import {
  ConnectionStatus,
  DestinationRead,
  DestinationSnippetRead,
  JobStatus,
  SourceRead,
  SourceSnippetRead,
  WebBackendConnectionListItem,
} from "core/request/AirbyteClient";

import { EntityTableDataItem, ITableDataItem, Status as ConnectionSyncStatus } from "./types";

const getConnectorTypeName = (connectorSpec: DestinationSnippetRead | SourceSnippetRead) => {
  return "sourceName" in connectorSpec ? connectorSpec.sourceName : connectorSpec.destinationName;
};

const getConnectorTypeId = (connectorSpec: DestinationSnippetRead | SourceSnippetRead) => {
  return "sourceId" in connectorSpec ? connectorSpec.sourceId : connectorSpec.destinationId;
};

// TODO: types in next methods look a bit ugly
export function getEntityTableData<
  S extends "source" | "destination",
  SoD extends S extends "source" ? SourceRead : DestinationRead
>(entities: SoD[], connections: WebBackendConnectionListItem[], type: S): EntityTableDataItem[] {
  const connectType = type === "source" ? "destination" : "source";

  const mappedEntities = entities.map((entityItem) => {
    const entitySoDId = entityItem[`${type}Id` as keyof SoD] as unknown as string;
    const entitySoDName = entityItem[`${type}Name` as keyof SoD] as unknown as string;
    const entityConnections = connections.filter(
      (connectionItem) => getConnectorTypeId(connectionItem[type]) === entitySoDId
    );

    if (!entityConnections.length) {
      return {
        entityId: entitySoDId,
        entityName: entityItem.name,
        enabled: true,
        connectorName: entitySoDName,
        connectorIcon: entityItem.icon,
        lastSync: null,
        connectEntities: [],
      };
    }

    const connectEntities = entityConnections.map((connection) => ({
      name: connection[connectType]?.name || "",
      connector: getConnectorTypeName(connection[connectType]),
      status: connection.status,
      lastSyncStatus: getConnectionSyncStatus(connection.status, connection.latestSyncJobStatus),
    }));

    const sortBySync = entityConnections.sort((item1, item2) =>
      item1.latestSyncJobCreatedAt && item2.latestSyncJobCreatedAt
        ? item2.latestSyncJobCreatedAt - item1.latestSyncJobCreatedAt
        : 0
    );

    return {
      entityId: entitySoDId,
      entityName: entityItem.name,
      enabled: true,
      connectorName: entitySoDName,
      lastSync: sortBySync?.[0].latestSyncJobCreatedAt,
      connectEntities,
      connectorIcon: entityItem.icon,
    };
  });

  return mappedEntities;
}

export const getConnectionTableData = (
  connections: WebBackendConnectionListItem[],
  type: "source" | "destination" | "connection"
): ITableDataItem[] => {
  const connectType = type === "source" ? "destination" : "source";

  return connections.map((connection) => ({
    connectionId: connection.connectionId,
    name: connection.name,
    entityName:
      type === "connection"
        ? `${connection.source?.sourceName} - ${connection.source?.name}`
        : connection[connectType]?.name || "",
    connectorName:
      type === "connection"
        ? `${connection.destination?.destinationName} - ${connection.destination?.name}`
        : getConnectorTypeName(connection[connectType]),
    lastSync: connection.latestSyncJobCreatedAt,
    enabled: connection.status === ConnectionStatus.active,
    schemaChange: connection.schemaChange,
    scheduleData: connection.scheduleData,
    scheduleType: connection.scheduleType,
    status: connection.status,
    isSyncing: connection.isSyncing,
    lastSyncStatus: getConnectionSyncStatus(connection.status, connection.latestSyncJobStatus),
    connectorIcon: type === "destination" ? connection.source.icon : connection.destination.icon,
    entityIcon: type === "destination" ? connection.destination.icon : connection.source.icon,
  }));
};

export const getConnectionSyncStatus = (
  status: ConnectionStatus,
  lastSyncJobStatus: JobStatus | undefined
): ConnectionSyncStatus => {
  if (status === ConnectionStatus.inactive) {
    return ConnectionSyncStatus.INACTIVE;
  }

  switch (lastSyncJobStatus) {
    case JobStatus.succeeded:
      return ConnectionSyncStatus.ACTIVE;

    case JobStatus.failed:
      return ConnectionSyncStatus.FAILED;

    case JobStatus.cancelled:
      return ConnectionSyncStatus.CANCELLED;

    case JobStatus.pending:
    case JobStatus.running:
      return ConnectionSyncStatus.PENDING;

    default:
      return ConnectionSyncStatus.EMPTY;
  }
};
