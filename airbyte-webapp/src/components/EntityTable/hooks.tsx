import { useSyncConnection } from "hooks/services/useConnectionHook";

import { WebBackendConnectionRead } from "../../core/request/AirbyteClient";

const useSyncActions = (): {
  syncManualConnection: (connection: WebBackendConnectionRead) => Promise<void>;
} => {
  const { mutateAsync: syncConnection } = useSyncConnection();

  const syncManualConnection = async (connection: WebBackendConnectionRead) => {
    await syncConnection(connection);
  };

  return { syncManualConnection };
};
export default useSyncActions;
