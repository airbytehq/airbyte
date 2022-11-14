import { DestinationDefinitionRead, SourceDefinitionRead } from "core/request/AirbyteClient";
import { SCOPE_WORKSPACE } from "services/Scope";

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

  return useSuspenseQuery(connectorDefinitionKeys.lists(), async () => {
    const [{ sourceDefinitions }, { destinationDefinitions }] = await Promise.all([
      sourceService.list(),
      destinationService.list(),
    ]);

    return { sourceDefinitions, destinationDefinitions };
  });
};
