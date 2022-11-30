import { useSyncConnection } from "hooks/services/useConnectionHook";

import { WebBackendConnectionListItem } from "../../core/request/AirbyteClient";

const useSyncActions = (): {
  syncManualConnection: (connection: WebBackendConnectionListItem) => Promise<void>;
} => {
  const { mutateAsync: syncConnection } = useSyncConnection();

  const syncManualConnection = async (connection: WebBackendConnectionListItem) => {
    await syncConnection(connection);
  };

  return { syncManualConnection };
};
export default useSyncActions;
