import FrequencyConfig from "config/FrequencyConfig.json";
import { Connection, ConnectionStatus } from "core/domain/connection";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useSyncConnection, useUpdateConnection } from "hooks/services/useConnectionHook";

const useSyncActions = (): {
  changeStatus: (connection: Connection) => Promise<void>;
  syncManualConnection: (connection: Connection) => Promise<void>;
} => {
  const { mutateAsync: updateConnection } = useUpdateConnection();
  const { mutateAsync: syncConnection } = useSyncConnection();
  const analyticsService = useAnalyticsService();

  const changeStatus = async (connection: Connection) => {
    await updateConnection({
      connectionId: connection.connectionId,
      syncCatalog: connection.syncCatalog,
      prefix: connection.prefix,
      schedule: connection.schedule || null,
      namespaceDefinition: connection.namespaceDefinition,
      namespaceFormat: connection.namespaceFormat,
      operations: connection.operations,
      status: connection.status === ConnectionStatus.ACTIVE ? ConnectionStatus.INACTIVE : ConnectionStatus.ACTIVE,
    });

    const frequency = FrequencyConfig.find(
      (item) => JSON.stringify(item.config) === JSON.stringify(connection.schedule)
    );

    analyticsService.track("Source - Action", {
      action: connection.status === "active" ? "Disable connection" : "Reenable connection",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      frequency: frequency?.text,
    });
  };

  const syncManualConnection = async (connection: Connection) => {
    await syncConnection(connection);
  };

  return { changeStatus, syncManualConnection };
};
export default useSyncActions;
