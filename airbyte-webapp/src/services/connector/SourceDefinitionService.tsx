import { QueryObserverSuccessResult, useQuery } from "react-query";

import { SourceDefinition } from "core/domain/connector";
import { useConfig } from "config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { SourceDefinitionService } from "core/domain/connector/SourceDefinitionService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

export const sourceDefinitionKeys = {
  all: ["sourceDefinition"] as const,
  lists: () => [...sourceDefinitionKeys.all, "list"] as const,
  detail: (id: string | number) =>
    [...sourceDefinitionKeys.all, "details", id] as const,
};

function useGetSourceDefinitionService(): SourceDefinitionService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () => new SourceDefinitionService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );
}

export const useGetSourceDefinition = (id: string): SourceDefinition => {
  const service = useGetSourceDefinitionService();

  return (useQuery(sourceDefinitionKeys.detail(id), () =>
    service.get(id)
  ) as QueryObserverSuccessResult<SourceDefinition>).data;
};

export const useListSourceDefinitions = (): SourceDefinition[] => {
  const service = useGetSourceDefinitionService();
  const workspace = useCurrentWorkspace();

  return (useQuery(sourceDefinitionKeys.lists(), () =>
    service.list(workspace.workspaceId)
  ) as QueryObserverSuccessResult<SourceDefinition[]>).data;
};
