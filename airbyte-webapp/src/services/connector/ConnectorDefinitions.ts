import { useConfig } from "config";
import { DestinationDefinitionRead, SourceDefinitionRead, webBackendCheckUpdates } from "core/request/AirbyteClient";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { SCOPE_WORKSPACE } from "services/Scope";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import { useGetDestinationDefinitionService } from "./DestinationDefinitionService";
import { useGetSourceDefinitionService } from "./SourceDefinitionService";
import { useSuspenseQuery } from "./useSuspenseQuery";

interface ConnectorSpecifications {
  sourceDefinitions: SourceDefinitionRead[];
  destinationDefinitions: DestinationDefinitionRead[];
}

export const connectorDefinitionKeys = {
  all: [SCOPE_WORKSPACE, "connectorDefinition"] as const,
  lists: () => [...connectorDefinitionKeys.all, "list"] as const,
  count: ["latestConnectorDefinitions"],
};

/**
 * Retrieve all source and destination specifications available in this instance.
 * This will include connector specifications which should temporarily be
 * forbidden to create new connections for. Those need to be filtered out with
 * {@code useAvailableConnectorDefinitions}.
 */
export const useConnectorSpecifications = (): ConnectorSpecifications => {
  const sourceService = useGetSourceDefinitionService();
  const destinationService = useGetDestinationDefinitionService();
  const workspaceId = useCurrentWorkspaceId();

  return useSuspenseQuery(connectorDefinitionKeys.lists(), async () => {
    const [{ sourceDefinitions }, { destinationDefinitions }] = await Promise.all([
      sourceService.list(workspaceId),
      destinationService.list(workspaceId),
    ]);

    return { sourceDefinitions, destinationDefinitions };
  });
};

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

export const useGetOutOfDateConnectorsCount = () => {
  const service = useConnectorService();
  return useSuspenseQuery(connectorDefinitionKeys.count, () => service.checkUpdates());
};
