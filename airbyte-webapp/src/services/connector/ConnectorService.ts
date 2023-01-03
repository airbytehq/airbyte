import { useConfig } from "config";
import { webBackendCheckUpdates } from "core/request/AirbyteClient";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

class ConnectorService extends AirbyteRequestService {
  checkUpdates() {
    return webBackendCheckUpdates(this.requestOptions);
  }
}

export function useConnectorService() {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new ConnectorService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}
