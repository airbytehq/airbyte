import { useConfig } from "config";
import { webBackendCheckUpdates, WebBackendCheckUpdatesRead } from "core/request/AirbyteClient";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { RequestMiddleware } from "core/request/RequestMiddleware";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

const NO_UPDATES: WebBackendCheckUpdatesRead = {
  destinationDefinitions: 0,
  sourceDefinitions: 0,
};

type EnabledFeatures = Partial<Record<FeatureItem, boolean>>;

class ConnectorService extends AirbyteRequestService {
  constructor(
    rootUrl: string,
    middlewares: RequestMiddleware[] = [],
    private readonly enabledFeatures: EnabledFeatures
  ) {
    super(rootUrl, middlewares);
    this.enabledFeatures = enabledFeatures;
  }
  checkUpdates() {
    if (this.enabledFeatures[FeatureItem.AllowUpdateConnectors]) {
      return webBackendCheckUpdates(this.requestOptions);
    }
    return Promise.resolve(NO_UPDATES);
  }
}

export function useConnectorService() {
  const { apiUrl } = useConfig();

  const enabledFeatures = {
    [FeatureItem.AllowUpdateConnectors]: useFeature(FeatureItem.AllowUpdateConnectors),
  };

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () => new ConnectorService(apiUrl, requestAuthMiddleware, enabledFeatures),
    [apiUrl, requestAuthMiddleware]
  );
}
