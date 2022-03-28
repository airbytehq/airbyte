import { useResource } from "rest-hooks";

import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import useWorkspace from "./useWorkspace";
import { DestinationDefinition } from "core/domain/connector";

const useDestinationDefinitionList = (): {
  destinationDefinitions: DestinationDefinition[];
} => {
  const { workspace } = useWorkspace();

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
