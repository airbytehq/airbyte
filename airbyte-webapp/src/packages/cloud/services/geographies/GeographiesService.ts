import { useConfig } from "config";
import { WebBackendGeographiesListResult } from "core/request/AirbyteClient";
import { GeographiesService } from "packages/cloud/lib/domain/geographies/GeographiesService";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { SCOPE_USER } from "services/Scope";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

export const workspaceKeys = {
  all: [SCOPE_USER, "geographies"] as const,
  list: () => [...workspaceKeys.all, "list"] as const,
};

export function useGeographiesService() {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new GeographiesService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}

/**
 * Returns a list of data geographies that can be associated with a connection or workspace
 **/
export function useAvailableGeographies() {
  const geographiesService = useGeographiesService();

  return useSuspenseQuery<WebBackendGeographiesListResult>(workspaceKeys.list(), () => geographiesService.list());
}
