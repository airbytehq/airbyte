import { Connection } from "../../core/resources/Connection";
import { Source } from "../../core/resources/Source";
import { Destination } from "../../core/resources/Destination";

export const getEntityTableData = (
  entities: Source[] | Destination[],
  connections: Connection[],
  type: "source" | "destination"
) => {
  const connectType = type === "source" ? "destination" : "source";

  // @ts-ignore
  return entities.map((entityItem: any) => {
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
};

export const getConnectionTableData = (
  connections: Connection[],
  type: "source" | "destination"
) => {
  const connectType = type === "source" ? "destination" : "source";

  return connections.map((item) => ({
    connectionId: item.connectionId,
    entityName: item[connectType]?.name || "",
    // @ts-ignore
    connectorName: item[connectType]?.[`${connectType}Name`] || "",
    lastSync: item.lastSync,
    enabled: item.status === "active",
    schedule: item.schedule,
    isSyncing: item.isSyncing,
  }));
};
