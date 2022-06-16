import { getFrequencyConfig } from "config/utils";
import { buildConnectionUpdate } from "core/domain/connection";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";
import { useSyncConnection, useUpdateConnection } from "hooks/services/useConnectionHook";
import { LegacyTrackActionType, TrackActionActions, TrackActionNamespace, useTrackAction } from "hooks/useTrackAction";

import { ConnectionStatus, WebBackendConnectionRead } from "../../core/request/AirbyteClient";

const useSyncActions = (): {
  changeStatus: (connection: WebBackendConnectionRead) => Promise<void>;
  syncManualConnection: (connection: WebBackendConnectionRead) => Promise<void>;
} => {
  const { mutateAsync: updateConnection } = useUpdateConnection();
  const { mutateAsync: syncConnection } = useSyncConnection();
  const analyticsService = useAnalyticsService();
  const trackSourceAction = useTrackAction(TrackActionNamespace.SOURCE, LegacyTrackActionType.SOURCE);

  const changeStatus = async (connection: WebBackendConnectionRead) => {
    await updateConnection(
      buildConnectionUpdate(connection, {
        status: connection.status === ConnectionStatus.active ? ConnectionStatus.inactive : ConnectionStatus.active,
      })
    );

    const frequency = getFrequencyConfig(connection.schedule);

    const trackableAction =
      connection.status === ConnectionStatus.active ? TrackActionActions.DISABLE : TrackActionActions.REENABLE;

    const trackableActionString = `${trackableAction} connection`;

    trackSourceAction(trackableActionString, [trackableAction], {
      frequency: frequency?.type,
      connector_source: connection.source?.sourceName,
      connector_source_definition_id: connection.source?.sourceDefinitionId, //another place I'm changing a label... clarify if that's ok
      connector_destination: connection.destination?.name,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
    });
  };

  const syncManualConnection = async (connection: WebBackendConnectionRead) => {
    await syncConnection(connection);
  };

  return { changeStatus, syncManualConnection };
};
export default useSyncActions;
