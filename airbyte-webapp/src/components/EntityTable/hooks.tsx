import { useFetcher } from "rest-hooks";

import FrequencyConfig from "config/FrequencyConfig.json";
import ConnectionResource, { Connection } from "core/resources/Connection";
import useConnection from "hooks/services/useConnectionHook";
import { Status } from "./types";
import { useAnalytics } from "hooks/useAnalytics";

const useSyncActions = (): {
  changeStatus: (connection: Connection) => Promise<void>;
  syncManualConnection: (connection: Connection) => Promise<void>;
} => {
  const { updateConnection } = useConnection();
  const SyncConnection = useFetcher(ConnectionResource.syncShape());
  const analyticsService = useAnalytics();

  const changeStatus = async (connection: Connection) => {
    await updateConnection({
      connectionId: connection.connectionId,
      syncCatalog: connection.syncCatalog,
      prefix: connection.prefix,
      schedule: connection.schedule || null,
      namespaceDefinition: connection.namespaceDefinition,
      namespaceFormat: connection.namespaceFormat,
      operations: connection.operations,
      status:
        connection.status === Status.ACTIVE ? Status.INACTIVE : Status.ACTIVE,
    });

    const frequency = FrequencyConfig.find(
      (item) =>
        JSON.stringify(item.config) === JSON.stringify(connection.schedule)
    );

    analyticsService.track("Source - Action", {
      action:
        connection.status === "active"
          ? "Disable connection"
          : "Reenable connection",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequency?.text,
    });
  };

  const syncManualConnection = async (connection: Connection) => {
    analyticsService.track("Source - Action", {
      action: "Full refresh sync",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: "manual", // Only manual connections have this button
    });

    await SyncConnection({
      connectionId: connection.connectionId,
    });
  };

  return { changeStatus, syncManualConnection };
};
export default useSyncActions;
