import { useMutation, useQueryClient } from "react-query";

import { useConfig } from "config";
import { SourceDefinition } from "core/domain/connector";
import { CreateSourceDefinitionPayload, SourceDefinitionService } from "core/domain/connector/SourceDefinitionService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { isDefined } from "utils/common";

import { SCOPE_WORKSPACE } from "../Scope";
import { useSuspenseQuery } from "./useSuspenseQuery";

export const sourceDefinitionKeys = {
  all: [SCOPE_WORKSPACE, "sourceDefinition"] as const,
  lists: () => [...sourceDefinitionKeys.all, "list"] as const,
  detail: (id: string) => [...sourceDefinitionKeys.all, "details", id] as const,
};

function useGetSourceDefinitionService(): SourceDefinitionService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () => new SourceDefinitionService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );
}

const useSourceDefinitionList = (): {
  sourceDefinitions: SourceDefinition[];
} => {
  const service = useGetSourceDefinitionService();
  const workspace = useCurrentWorkspace();

  return useSuspenseQuery(sourceDefinitionKeys.lists(), async () => {
    const [definition, latestDefinition] = await Promise.all([
      service.list(workspace.workspaceId),
      service.listLatest(workspace.workspaceId),
    ]);

    const sourceDefinitions: SourceDefinition[] = definition.sourceDefinitions.map((source: SourceDefinition) => {
      const withLatest = latestDefinition.sourceDefinitions.find(
        (latestSource: SourceDefinition) => latestSource.sourceDefinitionId === source.sourceDefinitionId
      );

      return {
        ...source,
        latestDockerImageTag: withLatest?.dockerImageTag ?? "",
      };
    });

    return { sourceDefinitions };
  });
};

const useSourceDefinition = <T extends string | undefined>(
  id: T
): T extends string ? SourceDefinition : SourceDefinition | undefined => {
  const service = useGetSourceDefinitionService();

  return useSuspenseQuery(sourceDefinitionKeys.detail(id || ""), () => service.get(id || ""), {
    enabled: isDefined(id),
  });
};

const useCreateSourceDefinition = () => {
  const service = useGetSourceDefinitionService();
  const queryClient = useQueryClient();

  return useMutation<SourceDefinition, Error, CreateSourceDefinitionPayload>(
    (sourceDefinition) => service.create(sourceDefinition),
    {
      onSuccess: (data) => {
        queryClient.setQueryData(
          sourceDefinitionKeys.lists(),
          (oldData: { sourceDefinitions: SourceDefinition[] } | undefined) => ({
            sourceDefinitions: [data, ...(oldData?.sourceDefinitions ?? [])],
          })
        );
      },
    }
  );
};

const useUpdateSourceDefinition = () => {
  const service = useGetSourceDefinitionService();
  const queryClient = useQueryClient();

  return useMutation<
    SourceDefinition,
    Error,
    {
      sourceDefinitionId: string;
      dockerImageTag: string;
    }
  >((sourceDefinition) => service.update(sourceDefinition), {
    onSuccess: (data) => {
      queryClient.setQueryData(sourceDefinitionKeys.detail(data.sourceDefinitionId), data);

      queryClient.setQueryData(
        sourceDefinitionKeys.lists(),
        (oldData: { sourceDefinitions: SourceDefinition[] } | undefined) => ({
          sourceDefinitions:
            oldData?.sourceDefinitions.map((sd) => (sd.sourceDefinitionId === data.sourceDefinitionId ? data : sd)) ??
            [],
        })
      );
    },
  });
};

export { useSourceDefinition, useSourceDefinitionList, useCreateSourceDefinition, useUpdateSourceDefinition };
