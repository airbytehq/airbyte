import { QueryObserverResult, useQuery } from "react-query";

import { DestinationDefinitionSpecification } from "core/domain/connector";
import { useConfig } from "config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { DestinationDefinitionSpecificationService } from "core/domain/connector/DestinationDefinitionSpecificationService";
import { isDefined } from "utils/common";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import { SCOPE_WORKSPACE } from "../Scope";
import { useSuspenseQuery } from "./useSuspenseQuery";

export const destinationDefinitionSpecificationKeys = {
  all: [SCOPE_WORKSPACE, "destinationDefinitionSpecification"] as const,
  detail: (id: string | number) => [...destinationDefinitionSpecificationKeys.all, "details", id] as const,
};

function useGetService(): DestinationDefinitionSpecificationService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () => new DestinationDefinitionSpecificationService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );
}

export const useGetDestinationDefinitionSpecification = (id: string): DestinationDefinitionSpecification => {
  const service = useGetService();
  const { workspaceId } = useCurrentWorkspace();

  return useSuspenseQuery(destinationDefinitionSpecificationKeys.detail(id), () => service.get(id, workspaceId));
};

export const useGetDestinationDefinitionSpecificationAsync = (
  id: string | null
): QueryObserverResult<DestinationDefinitionSpecification, Error> => {
  const service = useGetService();
  const { workspaceId } = useCurrentWorkspace();

  const escapedId = id ?? "";
  return useQuery(destinationDefinitionSpecificationKeys.detail(escapedId), () => service.get(escapedId, workspaceId), {
    enabled: isDefined(id),
  });
};
