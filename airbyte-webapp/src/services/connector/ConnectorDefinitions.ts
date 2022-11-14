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
