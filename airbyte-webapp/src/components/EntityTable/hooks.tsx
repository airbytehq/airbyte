import { getFrequencyConfig } from "config/utils";
import { buildConnectionUpdate } from "core/domain/connection";
import { useSyncConnection, useUpdateConnection } from "hooks/services/useConnectionHook";
import { TrackActionLegacyType, TrackActionType, TrackActionNamespace, useTrackAction } from "hooks/useTrackAction";

import { ConnectionStatus, WebBackendConnectionRead } from "../../core/request/AirbyteClient";

const useSyncActions = (): {
  changeStatus: (connection: WebBackendConnectionRead) => Promise<void>;
  syncManualConnection: (connection: WebBackendConnectionRead) => Promise<void>;
} => {
  const { mutateAsync: updateConnection } = useUpdateConnection();
  const { mutateAsync: syncConnection } = useSyncConnection();
  const trackSourceAction = useTrackAction(TrackActionNamespace.CONNECTION, TrackActionLegacyType.SOURCE);

  const changeStatus = async (connection: WebBackendConnectionRead) => {
    await updateConnection(
      buildConnectionUpdate(connection, {
        status: connection.status === ConnectionStatus.active ? ConnectionStatus.inactive : ConnectionStatus.active,
      })
    );

    const frequency = getFrequencyConfig(connection.schedule);

    const enabledStreams = connection.syncCatalog.streams.filter((stream) => stream.config?.selected).length;

    const trackableAction =
      connection.status === ConnectionStatus.active ? TrackActionType.DISABLE : TrackActionType.REENABLE;

    const trackableActionString = `${trackableAction} connection`;

    trackSourceAction(trackableActionString, trackableAction, {
      frequency: frequency?.type,
      connector_source: connection.source?.sourceName,
      connector_source_definition_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
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
