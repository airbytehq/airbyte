import { Connection } from "core/resources/Connection";
import { Source } from "core/resources/Source";
import { Destination } from "core/resources/Destination";
import { ITableDataItem, EntityTableDataItem, Status } from "./types";

// TODO: types in next methods look a bit ugly
export function getEntityTableData<
  S extends "source" | "destination",
  SoD extends S extends "source" ? Source : Destination
>(entities: SoD[], connections: Connection[], type: S): EntityTableDataItem[] {
  const connectType = type === "source" ? "destination" : "source";

  const mappedEntities = entities.map((entityItem) => {
    const entitySoDId = (entityItem[
      `${type}Id` as keyof SoD
    ] as unknown) as string;
    const entitySoDName = (entityItem[
      `${type}Name` as keyof SoD
    ] as unknown) as string;
    const entityConnections = connections.filter(
      (connectionItem) =>
        connectionItem[`${type}Id` as "sourceId" | "destinationId"] ===
        entitySoDId
    );

    if (!entityConnections.length) {
      return {
        entityId: entitySoDId,
        entityName: entityItem.name,
        enabled: true,
        connectorName: entitySoDName,
        lastSync: null,
        connectEntities: [],
      };
    }

    const connectEntities = entityConnections.map((connection) => ({
      name: connection[connectType]?.name || "",
      // @ts-ignore ts is not that clever to infer such types
      connector: connection[connectType]?.[`${connectType}Name`] || "",
      status: connection.status,
    }));

    const sortBySync = entityConnections.sort((item1, item2) =>
      item1.lastSync && item2.lastSync ? item2.lastSync - item1.lastSync : 0
    );

    return {
      entityId: entitySoDId,
      entityName: entityItem.name,
      enabled: true,
      connectorName: entitySoDName,
      lastSync: sortBySync?.[0].lastSync,
      connectEntities: connectEntities,
    };
  });

  return mappedEntities;
}

export const getConnectionTableData = (
  connections: Connection[],
  type: "source" | "destination"
): ITableDataItem[] => {
  const connectType = type === "source" ? "destination" : "source";

  return connections.map((connection) => ({
    connectionId: connection.connectionId,
    entityName: connection[connectType]?.name || "",
    // @ts-ignore conditional types are not supported here
    connectorName: connection[connectType]?.[`${connectType}Name`] || "",
    lastSync: connection.lastSync,
    enabled: connection.status === Status.ACTIVE,
    schedule: connection.schedule,
    status: connection.status,
    isSyncing: connection.isSyncing,
  }));
};
