import {
  QueryObserverSuccessResult,
  useMutation,
  useQuery,
  useQueryClient,
} from "react-query";

import { DestinationDefinition } from "core/domain/connector";
import { useConfig } from "config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import {
  CreateDestinationDefinitionPayload,
  DestinationDefinitionService,
} from "core/domain/connector/DestinationDefinitionService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { isDefined } from "utils/common";
import { SCOPE_WORKSPACE } from "../Scope";

export const destinationDefinitionKeys = {
  all: [SCOPE_WORKSPACE, "destinationDefinition"] as const,
  lists: () => [...destinationDefinitionKeys.all, "list"] as const,
  detail: (id: string) =>
    [...destinationDefinitionKeys.all, "details", id] as const,
};

function useGetDestinationDefinitionService(): DestinationDefinitionService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () => new DestinationDefinitionService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );
}

const useDestinationDefinitionList = (): {
  destinationDefinitions: DestinationDefinition[];
} => {
  const service = useGetDestinationDefinitionService();
  const workspace = useCurrentWorkspace();

  return (useQuery(destinationDefinitionKeys.lists(), async () => {
    const [definition, latestDefinition] = await Promise.all([
      service.list(workspace.workspaceId),
      service.listLatest(workspace.workspaceId),
    ]);

    const destinationDefinitions: DestinationDefinition[] = definition.destinationDefinitions.map(
      (destination: DestinationDefinition) => {
        const withLatest = latestDefinition.destinationDefinitions.find(
          (latestDestination: DestinationDefinition) =>
            latestDestination.destinationDefinitionId ===
            destination.destinationDefinitionId
        );

        return {
          ...destination,
          latestDockerImageTag: withLatest?.dockerImageTag ?? "",
        };
      }
    );

    return { destinationDefinitions };
  }) as QueryObserverSuccessResult<{
    destinationDefinitions: DestinationDefinition[];
  }>).data;
};

const useDestinationDefinition = <T extends string | undefined>(
  id: T
): T extends string
  ? DestinationDefinition
  : DestinationDefinition | undefined => {
  const service = useGetDestinationDefinitionService();

  return (useQuery(
    destinationDefinitionKeys.detail(id || ""),
    () => service.get(id || ""),
    {
      enabled: isDefined(id),
    }
  ) as QueryObserverSuccessResult<DestinationDefinition>).data;
};

const useCreateDestinationDefinition = () => {
  const service = useGetDestinationDefinitionService();
  const queryClient = useQueryClient();

  return useMutation<
    DestinationDefinition,
    Error,
    CreateDestinationDefinitionPayload
  >((destinationDefinition) => service.create(destinationDefinition), {
    onSuccess: (data) => {
      queryClient.setQueryData(
        destinationDefinitionKeys.lists(),
        (
          oldData:
            | { destinationDefinitions: DestinationDefinition[] }
            | undefined
        ) => ({
          destinationDefinitions: [
            data,
            ...(oldData?.destinationDefinitions ?? []),
          ],
        })
      );
    },
  });
};

const useUpdateDestinationDefinition = () => {
  const service = useGetDestinationDefinitionService();
  const queryClient = useQueryClient();

  return useMutation<
    DestinationDefinition,
    Error,
    {
      destinationDefinitionId: string;
      dockerImageTag: string;
    }
  >((destinationDefinition) => service.update(destinationDefinition), {
    onSuccess: (data) => {
      queryClient.setQueryData(
        destinationDefinitionKeys.detail(data.destinationDefinitionId),
        data
      );

      queryClient.setQueryData(
        destinationDefinitionKeys.lists(),
        (
          oldData:
            | { destinationDefinitions: DestinationDefinition[] }
            | undefined
        ) => ({
          destinationDefinitions:
            oldData?.destinationDefinitions.map((sd) =>
              sd.destinationDefinitionId === data.destinationDefinitionId
                ? data
                : sd
            ) ?? [],
        })
      );
    },
  });
};

export {
  useDestinationDefinition,
  useDestinationDefinitionList,
  useCreateDestinationDefinition,
  useUpdateDestinationDefinition,
};
