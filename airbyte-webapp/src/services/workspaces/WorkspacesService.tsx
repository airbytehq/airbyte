import React, { useCallback, useContext, useMemo } from "react";
import {
  QueryObserverSuccessResult,
  useMutation,
  useQuery,
  useQueryClient,
} from "react-query";

import useRouter from "hooks/useRouter";
import { Workspace, WorkspaceService } from "core/domain/workspace";
import { RoutePaths } from "pages/routePaths";
import { useConfig } from "config";
import { useDefaultRequestMiddlewares } from "../useDefaultRequestMiddlewares";
import { useInitService } from "../useInitService";
import { SCOPE_USER, SCOPE_WORKSPACE } from "../Scope";

export const workspaceKeys = {
  all: [SCOPE_USER, "workspaces"] as const,
  lists: () => [...workspaceKeys.all, "list"] as const,
  list: (filters: string) => [...workspaceKeys.lists(), { filters }] as const,
  detail: (workspaceId: string) =>
    [...workspaceKeys.all, "details", workspaceId] as const,
};

type Context = {
  selectWorkspace: (workspaceId?: string | null | Workspace) => void;
  exitWorkspace: () => void;
};

export const WorkspaceServiceContext = React.createContext<Context | null>(
  null
);

const useSelectWorkspace = (): ((
  workspace?: string | null | Workspace
) => void) => {
  const queryClient = useQueryClient();
  const { push } = useRouter();

  return useCallback(
    async (workspace) => {
      if (typeof workspace === "object") {
        push(`/${RoutePaths.Workspaces}/${workspace?.workspaceId}`);
      } else {
        push(`/${RoutePaths.Workspaces}/${workspace}`);
      }
      await queryClient.removeQueries(SCOPE_WORKSPACE);
    },
    [push, queryClient]
  );
};

export const WorkspaceServiceProvider: React.FC = ({ children }) => {
  const selectWorkspace = useSelectWorkspace();

  const ctx = useMemo<Context>(
    () => ({
      selectWorkspace,
      exitWorkspace: () => {
        selectWorkspace("");
      },
    }),
    [selectWorkspace]
  );

  return (
    <WorkspaceServiceContext.Provider value={ctx}>
      {children}
    </WorkspaceServiceContext.Provider>
  );
};

export const useWorkspaceService = (): Context => {
  const workspaceService = useContext(WorkspaceServiceContext);
  if (!workspaceService) {
    throw new Error(
      "useWorkspaceService must be used within a WorkspaceServiceProvider."
    );
  }

  return workspaceService;
};

function useWorkspaceApiService(): WorkspaceService {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new WorkspaceService(config.apiUrl, middlewares),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [config]
  );
}

export const useCurrentWorkspaceId = (): string => {
  const { params } = useRouter<unknown, { workspaceId: string }>();

  return params.workspaceId;
};

export const useCurrentWorkspace = (): Workspace => {
  const workspaceId = useCurrentWorkspaceId();

  return useGetWorkspace(workspaceId, {
    staleTime: Infinity,
  });
};

export const useListWorkspaces = (): Workspace[] => {
  const service = useWorkspaceApiService();

  return (useQuery(workspaceKeys.lists(), () =>
    service.list()
  ) as QueryObserverSuccessResult<{ workspaces: Workspace[] }>).data.workspaces;
};

export const useGetWorkspace = (
  workspaceId: string,
  options?: {
    staleTime: number;
  }
): Workspace => {
  const service = useWorkspaceApiService();

  return (useQuery(
    workspaceKeys.detail(workspaceId),
    () => service.get(workspaceId),
    options
  ) as QueryObserverSuccessResult<Workspace>).data;
};

export const useUpdateWorkspace = () => {
  const service = useWorkspaceApiService();
  const queryClient = useQueryClient();

  return useMutation(
    (workspace: Record<string, unknown>) => service.update(workspace),
    {
      onSuccess: (data) => {
        queryClient.setQueryData(workspaceKeys.detail(data.workspaceId), data);
      },
    }
  );
};
