import { useResource } from "rest-hooks";

import SourceDefinitionResource from "core/resources/SourceDefinition";
import { SourceDefinition } from "core/domain/connector";
import { useCurrentWorkspace } from "./useWorkspace";

const useSourceDefinitionList = (): {
  sourceDefinitions: SourceDefinition[];
} => {
  const workspace = useCurrentWorkspace();
  return useResource(SourceDefinitionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
};

const useSourceDefinition = (id: string): SourceDefinition => {
  return useResource(SourceDefinitionResource.detailShape(), {
    sourceDefinitionId: id,
  });
};

export { useSourceDefinitionList, useSourceDefinition };
