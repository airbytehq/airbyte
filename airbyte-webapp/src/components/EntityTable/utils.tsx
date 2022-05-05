import { Connection, ConnectionStatus } from "core/domain/connection";
import { Destination, DestinationDefinition, Source, SourceDefinition } from "core/domain/connector";
import Status from "core/statuses";

import { EntityTableDataItem, ITableDataItem, Status as ConnectionSyncStatus } from "./types";

// TODO: types in next methods look a bit ugly
export function getEntityTableData<
  S extends "source" | "destination",
  SoD extends S extends "source" ? Source : Destination,
  Def extends S extends "source" ? SourceDefinition : DestinationDefinition
>(entities: SoD[], connections: Connection[], definitions: Def[], type: S): EntityTableDataItem[] {
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
      // @ts-ignore ts is not that clever to infer such types
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
      connectEntities: connectEntities,
      connectorIcon: definition?.icon,
    };
  });

  return mappedEntities;
}

export const getConnectionTableData = (
  connections: Connection[],
  sourceDefinitions: SourceDefinition[],
  destinationDefinitions: DestinationDefinition[],
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
      entityName:
        type === "connection"
          ? `${connection.source?.sourceName} - ${connection.source?.name}`
          : connection[connectType]?.name || "",
      connectorName:
        type === "connection"
          ? `${connection.destination?.destinationName} - ${connection.destination?.name}`
          : // @ts-ignore conditional types are not supported here
            connection[connectType]?.[`${connectType}Name`] || "",
      lastSync: connection.latestSyncJobCreatedAt,
      enabled: connection.status === ConnectionStatus.ACTIVE,
      schedule: connection.schedule,
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
  lastSyncJobStatus: Status | null
): ConnectionSyncStatus => {
  if (status === ConnectionStatus.INACTIVE) return ConnectionSyncStatus.INACTIVE;

  switch (lastSyncJobStatus) {
    case Status.SUCCEEDED:
      return ConnectionSyncStatus.ACTIVE;

    case Status.FAILED:
    case Status.CANCELLED:
      return ConnectionSyncStatus.FAILED;

    case Status.PENDING:
    case Status.RUNNING:
      return ConnectionSyncStatus.PENDING;

    default:
      return ConnectionSyncStatus.EMPTY;
  }
};
