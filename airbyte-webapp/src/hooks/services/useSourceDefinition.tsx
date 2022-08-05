import { useResource } from "rest-hooks";

import SourceDefinitionResource from "core/resources/SourceDefinition";
import useWorkspace from "./useWorkspace";
import { SourceDefinition } from "core/domain/connector";

const useSourceDefinitionList = (): {
  sourceDefinitions: SourceDefinition[];
} => {
  const { workspace } = useWorkspace();

  return useResource(SourceDefinitionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

export { useSourceDefinitionList };
