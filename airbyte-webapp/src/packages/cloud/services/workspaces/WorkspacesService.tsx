import {
  QueryObserverResult,
  useMutation,
  useQuery,
  useQueryClient,
} from "react-query";

import type {
  CloudWorkspace,
  CloudWorkspaceUsage,
} from "packages/cloud/lib/domain/cloudWorkspaces/types";

import { CloudWorkspacesService } from "packages/cloud/lib/domain/cloudWorkspaces/CloudWorkspacesService";
import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useConfig } from "packages/cloud/services/config";
import { useDefaultRequestMiddlewares } from "packages/cloud/services/useDefaultRequestMiddlewares";
import { useInitService } from "packages/cloud/services/useInitService";
import { QueryObserverSuccessResult } from "react-query/types/core/types";

export const workspaceKeys = {
  all: ["cloud_workspaces"] as const,
  lists: () => [...workspaceKeys.all, "list"] as const,
  list: (filters: string) => [...workspaceKeys.lists(), { filters }] as const,
  details: () => [...workspaceKeys.all, "detail"] as const,
  detail: (id: number | string) => [...workspaceKeys.details(), id] as const,
  usage: (id: number | string) =>
    [...workspaceKeys.details(), id, "usage"] as const,
};

function useGetWorkspaceService(): CloudWorkspacesService {
  const { cloudApiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(
    () => new CloudWorkspacesService(cloudApiUrl, requestAuthMiddleware),
    [cloudApiUrl, requestAuthMiddleware]
  );
}

export function useListCloudWorkspaces(): CloudWorkspace[] {
  const service = useGetWorkspaceService();
  const user = useCurrentUser();

  return (useQuery<CloudWorkspace[]>(workspaceKeys.lists(), () =>
    service.listByUser(user.userId)
  ) as QueryObserverSuccessResult<CloudWorkspace[]>).data;
}

export function useCreateWorkspace() {
  const service = useGetWorkspaceService();
  const queryClient = useQueryClient();
  const user = useCurrentUser();

  return useMutation(
    async (name: string) => service.create({ name, userId: user.userId }),
    {
      onSuccess: (result) => {
        queryClient.setQueryData<CloudWorkspace[]>(
          workspaceKeys.lists(),
          (old) => [...(old ?? []), result]
        );
      },
    }
  ).mutateAsync;
}

export function useUpdateWorkspace() {
  const service = useGetWorkspaceService();
  const queryClient = useQueryClient();

  return useMutation(
    async (payload: { workspaceId: string; name: string }) =>
      service.update(payload.workspaceId, { name: payload.name }),
    {
      onSuccess: (result) => {
        queryClient.setQueryData<CloudWorkspace[]>(
          workspaceKeys.lists(),
          (old) => {
            const list = old ?? [];
            if (list.length === 0) {
              return [result];
            }

            const index = list.findIndex(
              (item) => item.workspaceId === result.workspaceId
            );

            if (index === -1) {
              return list;
            }

            return [...list.slice(0, index), result, ...list.slice(index + 1)];
          }
        );

        queryClient.setQueryData<CloudWorkspace>(
          [workspaceKeys.detail(result.workspaceId)],
          (old) => {
            return {
              ...old,
              ...result,
            };
          }
        );
      },
    }
  );
}

export function useRemoveWorkspace() {
  const service = useGetWorkspaceService();
  const queryClient = useQueryClient();

  return useMutation(
    async (workspaceId: string) => service.remove(workspaceId),
    {
      onSuccess: (_, workspaceId) => {
        queryClient.setQueryData<CloudWorkspace[] | undefined>(
          workspaceKeys.lists(),
          (old) =>
            old?.filter((workspace) => workspace.workspaceId !== workspaceId)
        );
      },
    }
  );
}

export function useGetCloudWorkspace(workspaceId: string): CloudWorkspace {
  const service = useGetWorkspaceService();

  return (useQuery<CloudWorkspace>([workspaceKeys.detail(workspaceId)], () =>
    service.get(workspaceId)
  ) as QueryObserverSuccessResult<CloudWorkspace>).data;
}

export function useGetUsage(
  workspaceId: string
): QueryObserverResult<CloudWorkspaceUsage> {
  const service = useGetWorkspaceService();

  return useQuery<CloudWorkspaceUsage>([workspaceKeys.usage(workspaceId)], () =>
    service.getUsage(workspaceId)
  );
}

export { useWorkspaceService } from "services/workspaces/WorkspacesService";
