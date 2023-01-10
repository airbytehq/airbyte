import { DestinationDefinitionRead, SourceDefinitionRead } from "core/request/AirbyteClient";
import { SCOPE_WORKSPACE } from "services/Scope";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import { useConnectorService } from "./ConnectorService";
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
  count: () => [...connectorDefinitionKeys.all, "count"] as const,
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

export const useGetOutOfDateConnectorsCount = () => {
  const service = useConnectorService();
  return useSuspenseQuery(connectorDefinitionKeys.count(), () => service.checkUpdates());
};
