import { useResource } from "rest-hooks";

import SourceDefinitionResource, {
  SourceDefinition,
} from "core/resources/SourceDefinition";
import useWorkspace from "./useWorkspace";

const useSourceDefinitionList = (): {
  sourceDefinitions: SourceDefinition[];
} => {
  const { workspace } = useWorkspace();

  return useResource(SourceDefinitionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

export { useSourceDefinitionList };
