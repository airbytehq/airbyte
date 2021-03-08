import { useFetcher } from "rest-hooks";

import config from "config";
import FrequencyConfig from "data/FrequencyConfig.json";
import { AnalyticsService } from "core/analytics/AnalyticsService";
import ConnectionResource, { Connection } from "core/resources/Connection";
import useConnection from "components/hooks/services/useConnectionHook";
import { Status } from "./types";

const useSyncActions = (): {
  changeStatus: (connection: Connection) => Promise<void>;
  syncManualConnection: (connection: Connection) => Promise<void>;
} => {
  const { updateConnection } = useConnection();
  const SyncConnection = useFetcher(ConnectionResource.syncShape());

  const changeStatus = async (connection: Connection) => {
    await updateConnection({
      connectionId: connection.connectionId,
      syncCatalog: connection.syncCatalog,
      prefix: connection.prefix,
      schedule: connection.schedule || null,
      status:
        connection.status === Status.ACTIVE ? Status.INACTIVE : Status.ACTIVE,
    });

    const frequency = FrequencyConfig.find(
      (item) =>
        JSON.stringify(item.config) === JSON.stringify(connection.schedule)
    );

    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
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
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Full refresh sync",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: "manual", // Only manual connections have this button
    });

    SyncConnection({
      connectionId: connection.connectionId,
    });
  };

  return { changeStatus, syncManualConnection };
};
export default useSyncActions;
