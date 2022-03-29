import { useResource } from "rest-hooks";

import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import { DestinationDefinition } from "core/domain/connector";
import { useCurrentWorkspace } from "./useWorkspace";

const useDestinationDefinitionList = (): {
  destinationDefinitions: DestinationDefinition[];
} => {
  const workspace = useCurrentWorkspace();
  return useResource(DestinationDefinitionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

const useDestinationDefinition = (id: string): DestinationDefinition => {
  return useResource(DestinationDefinitionResource.detailShape(), {
    destinationDefinitionId: id,
  });
};

export { useDestinationDefinitionList, useDestinationDefinition };
