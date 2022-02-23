import { useResource } from "rest-hooks";

import DestinationDefinitionResource, {
  DestinationDefinition,
} from "core/resources/DestinationDefinition";
import useWorkspace from "./useWorkspace";

const useDestinationDefinitionList = (): {
  destinationDefinitions: DestinationDefinition[];
} => {
  const { workspace } = useWorkspace();

  return useResource(DestinationDefinitionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

export { useDestinationDefinitionList };
