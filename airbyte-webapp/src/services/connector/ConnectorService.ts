import { useConfig } from "config";
import { webBackendCheckUpdates, WebBackendCheckUpdatesRead } from "core/request/AirbyteClient";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { isCloudApp } from "utils/app";

class ConnectorService extends AirbyteRequestService {
  checkUpdates(): Promise<WebBackendCheckUpdatesRead> {
    if (isCloudApp()) {
      return Promise.resolve({ sourceDefinitions: 0, destinationDefinitions: 0 });
    }
    return webBackendCheckUpdates(this.requestOptions);
  }
}

export function useConnectorService() {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new ConnectorService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}
