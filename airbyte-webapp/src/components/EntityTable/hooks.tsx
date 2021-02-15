import { useFetcher } from "rest-hooks";

import FrequencyConfig from "../../data/FrequencyConfig.json";
import { AnalyticsService } from "../../core/analytics/AnalyticsService";
import config from "../../config";
import ConnectionResource, {
  Connection
} from "../../core/resources/Connection";
import useConnection from "../hooks/services/useConnectionHook";

const useSyncActions = () => {
  const { updateConnection } = useConnection();
  const SyncConnection = useFetcher(ConnectionResource.syncShape());

  const changeStatus = async (connection: Connection) => {
    await updateConnection({
      connectionId: connection.connectionId,
      syncCatalog: connection.syncCatalog,
      schedule: connection.schedule || null,
      status: connection.status === "active" ? "inactive" : "active"
    });

    const frequency = FrequencyConfig.find(
      item =>
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
      frequency: frequency?.text
    });
  };

  const syncManualConnection = (connection: Connection) => {
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Full refresh sync",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: "manual" // Only manual connections have this button
    });

    SyncConnection({
      connectionId: connection.connectionId
    });
  };

  return { changeStatus, syncManualConnection };
};

export default useSyncActions;
