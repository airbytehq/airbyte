import { useMutation, useQueryClient } from "react-query";

import { useConfig } from "config";
import { DestinationDefinitionService } from "core/domain/connector/DestinationDefinitionService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import { isDefined } from "utils/common";

import { connectorDefinitionKeys } from "./ConnectorDefinitions";
import { useSuspenseQuery } from "./useSuspenseQuery";
import { DestinationDefinitionCreate, DestinationDefinitionRead } from "../../core/request/AirbyteClient";
import { SCOPE_WORKSPACE } from "../Scope";

export const destinationDefinitionKeys = {
  all: [SCOPE_WORKSPACE, "destinationDefinition"] as const,
  lists: () => [...destinationDefinitionKeys.all, "list"] as const,
  detail: (id: string) => [...destinationDefinitionKeys.all, "details", id] as const,
};

export function useGetDestinationDefinitionService(): DestinationDefinitionService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () => new DestinationDefinitionService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );
}

export interface DestinationDefinitionReadWithLatestTag extends DestinationDefinitionRead {
  latestDockerImageTag?: string;
}

const useDestinationDefinitionList = (): {
  destinationDefinitions: DestinationDefinitionReadWithLatestTag[];
} => {
  const service = useGetDestinationDefinitionService();
  const workspaceId = useCurrentWorkspaceId();

  return useSuspenseQuery(destinationDefinitionKeys.lists(), async () => {
    const [definition, latestDefinition] = await Promise.all([service.list(workspaceId), service.listLatest()]);

    const destinationDefinitions: DestinationDefinitionRead[] = definition.destinationDefinitions.map(
      (destination: DestinationDefinitionRead) => {
        const withLatest = latestDefinition.destinationDefinitions.find(
          (latestDestination) => latestDestination.destinationDefinitionId === destination.destinationDefinitionId
        );

        return {
          ...destination,
          latestDockerImageTag: withLatest?.dockerImageTag,
        };
      }
    );

    return { destinationDefinitions };
  });
};

const useDestinationDefinition = <T extends string | undefined>(
  destinationDefinitionId: T
): T extends string ? DestinationDefinitionRead : DestinationDefinitionRead | undefined => {
  const service = useGetDestinationDefinitionService();
  const workspaceId = useCurrentWorkspaceId();

  return useSuspenseQuery(
    destinationDefinitionKeys.detail(destinationDefinitionId || ""),
    () => service.get({ workspaceId, destinationDefinitionId: destinationDefinitionId || "" }),
    {
      enabled: isDefined(destinationDefinitionId),
    }
  );
};

const useCreateDestinationDefinition = () => {
  const service = useGetDestinationDefinitionService();
  const queryClient = useQueryClient();
  const workspaceId = useCurrentWorkspaceId();

  return useMutation<DestinationDefinitionRead, Error, DestinationDefinitionCreate>(
    (destinationDefinition) => service.createCustom({ workspaceId, destinationDefinition }),
    {
      onSuccess: (data) => {
        queryClient.setQueryData(
          destinationDefinitionKeys.lists(),
          (oldData: { destinationDefinitions: DestinationDefinitionRead[] } | undefined) => ({
            destinationDefinitions: [data, ...(oldData?.destinationDefinitions ?? [])],
          })
        );
      },
    }
  );
};

const useUpdateDestinationDefinition = () => {
  const service = useGetDestinationDefinitionService();
  const queryClient = useQueryClient();

  return useMutation<
    DestinationDefinitionRead,
    Error,
    {
      destinationDefinitionId: string;
      dockerImageTag: string;
    }
  >((destinationDefinition) => service.update(destinationDefinition), {
    onSuccess: (data) => {
      queryClient.setQueryData(destinationDefinitionKeys.detail(data.destinationDefinitionId), data);

      queryClient.setQueryData(
        destinationDefinitionKeys.lists(),
        (oldData: { destinationDefinitions: DestinationDefinitionRead[] } | undefined) => ({
          destinationDefinitions:
            oldData?.destinationDefinitions.map((sd) =>
              sd.destinationDefinitionId === data.destinationDefinitionId ? data : sd
            ) ?? [],
        })
      );

      queryClient.invalidateQueries(connectorDefinitionKeys.count());
    },
  });
};

export {
  useDestinationDefinition,
  useDestinationDefinitionList,
  useCreateDestinationDefinition,
  useUpdateDestinationDefinition,
};
