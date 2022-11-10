import React, { useCallback, useContext, useMemo } from "react";
import { useMutation, useQueryClient } from "react-query";
import { useNavigate, useParams } from "react-router-dom";

import { Workspace, WorkspaceService } from "core/domain/workspace";
import { RoutePaths } from "pages/routePaths";

import { useConfig } from "../../config";
import { WorkspaceUpdate } from "../../core/request/AirbyteClient";
import { useSuspenseQuery } from "../connector/useSuspenseQuery";
import { SCOPE_USER, SCOPE_WORKSPACE } from "../Scope";
import { useDefaultRequestMiddlewares } from "../useDefaultRequestMiddlewares";
import { useInitService } from "../useInitService";

export const workspaceKeys = {
  all: [SCOPE_USER, "workspaces"] as const,
  lists: () => [...workspaceKeys.all, "list"] as const,
  list: (filters: string) => [...workspaceKeys.lists(), { filters }] as const,
  detail: (workspaceId: string) => [...workspaceKeys.all, "details", workspaceId] as const,
  state: (workspaceId: string) => [...workspaceKeys.all, "state", workspaceId] as const,
};

interface Context {
  selectWorkspace: (workspaceId?: string | null | Workspace) => void;
  exitWorkspace: () => void;
}

export const WorkspaceServiceContext = React.createContext<Context | null>(null);

const useSelectWorkspace = (): ((workspace?: string | null | Workspace) => void) => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useCallback(
    async (workspace) => {
      if (typeof workspace === "object") {
        navigate(`/${RoutePaths.Workspaces}/${workspace?.workspaceId}`);
      } else {
        navigate(`/${RoutePaths.Workspaces}/${workspace}`);
      }
      queryClient.removeQueries(SCOPE_WORKSPACE);
    },
    [navigate, queryClient]
  );
};

export const WorkspaceServiceProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
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

  return <WorkspaceServiceContext.Provider value={ctx}>{children}</WorkspaceServiceContext.Provider>;
};

export const useWorkspaceService = (): Context => {
  const workspaceService = useContext(WorkspaceServiceContext);
  if (!workspaceService) {
    throw new Error("useWorkspaceService must be used within a WorkspaceServiceProvider.");
  }

  return workspaceService;
};

function useWorkspaceApiService() {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();
  return useInitService(() => new WorkspaceService(config.apiUrl, middlewares), [config.apiUrl, middlewares]);
}

export const useCurrentWorkspaceId = () => {
  const params = useParams<{ workspaceId: string }>();

  return params.workspaceId as string;
};

export const useCurrentWorkspace = () => {
  const workspaceId = useCurrentWorkspaceId();

  return useGetWorkspace(workspaceId, {
    staleTime: Infinity,
  });
};

export const useCurrentWorkspaceState = () => {
  const workspaceId = useCurrentWorkspaceId();
  const service = useWorkspaceApiService();

  return useSuspenseQuery(workspaceKeys.state(workspaceId), () => service.getState({ workspaceId }), {
    // We want to keep this query only shortly in cache, so we refetch
    // the data whenever the user might have changed sources/destinations/connections
    // without requiring to manually invalidate that query on each change.
    cacheTime: 5 * 1000,
  });
};

export const useListWorkspaces = () => {
  const service = useWorkspaceApiService();

  return useSuspenseQuery(workspaceKeys.lists(), () => service.list()).workspaces;
};

export const useGetWorkspace = (
  workspaceId: string,
  options?: {
    staleTime: number;
  }
) => {
  const service = useWorkspaceApiService();
  return useSuspenseQuery(workspaceKeys.detail(workspaceId), () => service.get({ workspaceId }), options);
};

export const useUpdateWorkspace = () => {
  const service = useWorkspaceApiService();
  const queryClient = useQueryClient();

  return useMutation((workspace: WorkspaceUpdate) => service.update(workspace), {
    onSuccess: (data) => {
      queryClient.setQueryData(workspaceKeys.detail(data.workspaceId), data);
    },
  });
};

export const useInvalidateWorkspace = (workspaceId: string) => {
  const queryClient = useQueryClient();

  return useCallback(
    () => queryClient.invalidateQueries(workspaceKeys.detail(workspaceId)),
    [queryClient, workspaceId]
  );
};
