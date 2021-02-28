import { Connection } from "core/resources/Connection";
import { Source } from "core/resources/Source";
import { Destination } from "core/resources/Destination";
import { ITableDataItem, EntityTableDataItem } from "./types";

export const getEntityTableData = (
  entities: Source[] | Destination[],
  connections: Connection[],
  type: "source" | "destination"
): EntityTableDataItem[] => {
  const connectType = type === "source" ? "destination" : "source";

  // @ts-ignore
  const mappedEntities = entities.map((entityItem: any) => {
    const entityConnections = connections.filter(
      (connectionItem: any) =>
        connectionItem[`${type}Id`] === entityItem[`${type}Id`]
    );

    if (!entityConnections.length) {
      return {
        entityId: entityItem[`${type}Id`],
        entityName: entityItem.name,
        enabled: true,
        connectorName: entityItem[`${type}Name`],
        lastSync: null,
        connectEntities: [],
      };
    }

    const connectEntities = entityConnections.map((item: any) => ({
      name: item[connectType]?.name || "",
      connector: item[connectType]?.[`${connectType}Name`] || "",
    }));

    const sortBySync = entityConnections.sort((item1, item2) =>
      item1.lastSync && item2.lastSync ? item2.lastSync - item1.lastSync : 0
    );

    return {
      entityId: entityItem[`${type}Id`],
      entityName: entityItem.name,
      enabled: true,
      connectorName: entityItem[`${type}Name`],
      lastSync: sortBySync?.[0].lastSync,
      connectEntities: connectEntities,
    };
  });

  return mappedEntities;
};

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
    enabled: connection.status === "active",
    schedule: connection.schedule,
    isSyncing: connection.isSyncing,
  }));
};
