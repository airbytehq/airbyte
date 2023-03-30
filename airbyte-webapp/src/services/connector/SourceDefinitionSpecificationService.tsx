import { useQuery } from "react-query";

import { useUser } from "core/AuthContext";
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
  const { removeUser } = useUser();
  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () =>
      new SourceDefinitionSpecificationService(
        process.env.REACT_APP_API_URL as string,
        requestAuthMiddleware,
        removeUser
      ),
    [process.env.REACT_APP_API_URL as string, requestAuthMiddleware, removeUser]
  );
}

export const useGetSourceDefinitionSpecification = (id: string) => {
  const service = useGetService();
  const { workspaceId } = useCurrentWorkspace();

  return useSuspenseQuery(sourceDefinitionSpecificationKeys.detail(id), () => service.get(id, workspaceId));
};

export const useGetSourceDefinitionSpecificationAsync = (id: string | null) => {
  const service = useGetService();
  const { workspaceId } = useCurrentWorkspace();

  const escapedId = id ?? "";
  return useQuery(sourceDefinitionSpecificationKeys.detail(escapedId), () => service.get(escapedId, workspaceId), {
    enabled: isDefined(id),
  });
};
