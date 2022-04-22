import { QueryObserverResult, useQuery } from "react-query";

import { useConfig } from "config";
import { SourceDefinitionSpecification } from "core/domain/connector";
import { SourceDefinitionSpecificationService } from "core/domain/connector/SourceDefinitionSpecificationService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { isDefined } from "utils/common";

import { SCOPE_WORKSPACE } from "../Scope";
import { useSuspenseQuery } from "./useSuspenseQuery";

export const sourceDefinitionSpecificationKeys = {
  all: [SCOPE_WORKSPACE, "sourceDefinitionSpecification"] as const,
  detail: (id: string | number) => [...sourceDefinitionSpecificationKeys.all, "details", id] as const,
};

function useGetService(): SourceDefinitionSpecificationService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () => new SourceDefinitionSpecificationService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );
}

export const useGetSourceDefinitionSpecification = (id: string): SourceDefinitionSpecification => {
  const service = useGetService();
  const { workspaceId } = useCurrentWorkspace();

  return useSuspenseQuery(sourceDefinitionSpecificationKeys.detail(id), () => service.get(id, workspaceId));
};

export const useGetSourceDefinitionSpecificationAsync = (
  id: string | null
): QueryObserverResult<SourceDefinitionSpecification, Error> => {
  const service = useGetService();
  const { workspaceId } = useCurrentWorkspace();

  const escapedId = id ?? "";
  return useQuery(sourceDefinitionSpecificationKeys.detail(escapedId), () => service.get(escapedId, workspaceId), {
    enabled: isDefined(id),
  });
};
