import {
  ConnectionStatus,
  DestinationDefinitionRead,
  DestinationRead,
  JobStatus,
  SourceDefinitionRead,
  SourceRead,
  WebBackendConnectionRead,
} from "../../core/request/AirbyteClient";
import { EntityTableDataItem, ITableDataItem, Status as ConnectionSyncStatus } from "./types";

// TODO: types in next methods look a bit ugly
export function getEntityTableData<
  S extends "source" | "destination",
  SoD extends S extends "source" ? SourceRead : DestinationRead,
  Def extends S extends "source" ? SourceDefinitionRead : DestinationDefinitionRead
>(entities: SoD[], connections: WebBackendConnectionRead[], definitions: Def[], type: S): EntityTableDataItem[] {
  const connectType = type === "source" ? "destination" : "source";

  const mappedEntities = entities.map((entityItem) => {
    const entitySoDId = entityItem[`${type}Id` as keyof SoD] as unknown as string;
    const entitySoDName = entityItem[`${type}Name` as keyof SoD] as unknown as string;
    const entityConnections = connections.filter(
      (connectionItem) => connectionItem[`${type}Id` as "sourceId" | "destinationId"] === entitySoDId
    );

    const definitionId = `${type}DefinitionId` as keyof Def;
    const entityDefinitionId = entityItem[`${type}DefinitionId` as keyof SoD];

    const definition = definitions.find(
      // @ts-expect-error ignored during react-scripts update
      (def) => def[definitionId] === entityDefinitionId
    );

    if (!entityConnections.length) {
      return {
        entityId: entitySoDId,
        entityName: entityItem.name,
        enabled: true,
        connectorName: entitySoDName,
        connectorIcon: definition?.icon,
        lastSync: null,
        connectEntities: [],
      };
    }

    const connectEntities = entityConnections.map((connection) => ({
      name: connection[connectType]?.name || "",
      // @ts-expect-error ts is not that clever to infer such types
      connector: connection[connectType]?.[`${connectType}Name`] || "",
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
      connectorIcon: definition?.icon,
    };
  });

  return mappedEntities;
}

export const getConnectionTableData = (
  connections: WebBackendConnectionRead[],
  sourceDefinitions: SourceDefinitionRead[],
  destinationDefinitions: DestinationDefinitionRead[],
  type: "source" | "destination" | "connection"
): ITableDataItem[] => {
  const connectType = type === "source" ? "destination" : "source";

  return connections.map((connection) => {
    const sourceIcon = sourceDefinitions.find(
      (definition) => definition.sourceDefinitionId === connection.source.sourceDefinitionId
    )?.icon;
    const destinationIcon = destinationDefinitions.find(
      (definition) => definition.destinationDefinitionId === connection.destination.destinationDefinitionId
    )?.icon;

    return {
      connectionId: connection.connectionId,
      name: connection.name,
      entityName:
        type === "connection"
          ? `${connection.source?.sourceName} - ${connection.source?.name}`
          : connection[connectType]?.name || "",
      connectorName:
        type === "connection"
          ? `${connection.destination?.destinationName} - ${connection.destination?.name}`
          : connection[connectType]?.name || "",
      lastSync: connection.latestSyncJobCreatedAt,
      enabled: connection.status === ConnectionStatus.active,
      schedule: connection.scheduleData?.basicSchedule,
      status: connection.status,
      isSyncing: connection.isSyncing,
      lastSyncStatus: getConnectionSyncStatus(connection.status, connection.latestSyncJobStatus),
      connectorIcon: type === "destination" ? sourceIcon : destinationIcon,
      entityIcon: type === "destination" ? destinationIcon : sourceIcon,
    };
  });
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
    case JobStatus.cancelled:
      return ConnectionSyncStatus.FAILED;

    case JobStatus.pending:
    case JobStatus.running:
      return ConnectionSyncStatus.PENDING;

    default:
      return ConnectionSyncStatus.EMPTY;
  }
};
