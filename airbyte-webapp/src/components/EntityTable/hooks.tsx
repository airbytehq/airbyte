import { getFrequencyType } from "config/utils";
import { Action, Namespace } from "core/analytics";
import { buildConnectionUpdate } from "core/domain/connection";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useSyncConnection, useUpdateConnection } from "hooks/services/useConnectionHook";

import { ConnectionStatus, WebBackendConnectionRead } from "../../core/request/AirbyteClient";

const useSyncActions = (): {
  changeStatus: (connection: WebBackendConnectionRead) => Promise<void>;
  syncManualConnection: (connection: WebBackendConnectionRead) => Promise<void>;
} => {
  const { mutateAsync: updateConnection } = useUpdateConnection();
  const { mutateAsync: syncConnection } = useSyncConnection();
  const analyticsService = useAnalyticsService();

  const changeStatus = async (connection: WebBackendConnectionRead) => {
    await updateConnection(
      buildConnectionUpdate(connection, {
        status: connection.status === ConnectionStatus.active ? ConnectionStatus.inactive : ConnectionStatus.active,
      })
    );

    const enabledStreams = connection.syncCatalog.streams.filter((stream) => stream.config?.selected).length;

    const trackableAction = connection.status === ConnectionStatus.active ? Action.DISABLE : Action.REENABLE;

    analyticsService.track(Namespace.CONNECTION, trackableAction, {
      frequency: getFrequencyType(connection.scheduleData?.basicSchedule),
      connector_source: connection.source?.sourceName,
      connector_source_definition_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      available_streams: connection.syncCatalog.streams.length,
      enabled_streams: enabledStreams,
    });
  };

  const syncManualConnection = async (connection: WebBackendConnectionRead) => {
    await syncConnection(connection);
  };

  return { changeStatus, syncManualConnection };
};
export default useSyncActions;
