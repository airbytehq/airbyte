import React, { useContext, useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";
import { useLocalStorage } from "react-use";
import { useResetter } from "rest-hooks";

import { CloudWorkspacesService } from "packages/cloud/lib/domain/cloudWorkspaces/CloudWorkspacesService";
import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useDefaultRequestMiddlewares } from "packages/cloud/services/useDefaultRequestMiddlewares";
import { CloudWorkspace } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useConfig } from "packages/cloud/services/config";

type Context = {
  currentWorkspaceId?: string | null;
  selectWorkspace: (workspaceId: string | null) => void;
  createWorkspace: (name: string) => Promise<CloudWorkspace>;
  removeWorkspace: {
    mutateAsync: (workspaceId: string) => Promise<void>;
    isLoading: boolean;
  };
};

export const WorkspaceServiceContext = React.createContext<Context | null>(
  null
);

function useGetWorkspaceService() {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  const { cloudApiUrl } = useConfig();

  return useMemo(
    () => new CloudWorkspacesService(cloudApiUrl, requestAuthMiddleware),
    [requestAuthMiddleware, cloudApiUrl]
  );
}

export function useListWorkspaces() {
  const service = useGetWorkspaceService();
  const user = useCurrentUser();

  return useQuery("workspaces", () => service.listByUser(user.userId), {
    suspense: true,
  });
}

export function useCreateWorkspace() {
  const service = useGetWorkspaceService();
  const queryClient = useQueryClient();

  return useMutation(
    async (payload: { name: string; userId: string }) =>
      service.create(payload),
    {
      onSuccess: (result) => {
        queryClient.setQueryData<CloudWorkspace[]>("workspaces", (old) => [
          ...(old ?? []),
          result,
        ]);
      },
    }
  ).mutateAsync;
}

export function useUpdateWorkspace() {
  const service = useGetWorkspaceService();
  const queryClient = useQueryClient();

  return useMutation(
    async (workspaceId: string) => service.update(workspaceId, { name: "" }),
    {
      onSuccess: (result) => {
        queryClient.setQueryData<CloudWorkspace[]>("workspaces", (old) => [
          ...(old ?? []),
          result,
        ]);
      },
    }
  ).mutateAsync;
}

export function useRemoveWorkspace() {
  const service = useGetWorkspaceService();
  const queryClient = useQueryClient();

  return useMutation(
    async (workspaceId: string) => service.remove(workspaceId),
    {
      onSuccess: (_, workspaceId) => {
        queryClient.setQueryData<CloudWorkspace[] | undefined>(
          "workspaces",
          (old) =>
            old?.filter((workspace) => workspace.workspaceId !== workspaceId)
        );
      },
    }
  );
}

export function useGetWorkspace(workspaceId: string) {
  const service = useGetWorkspaceService();

  return useQuery(["workspace", workspaceId], () => service.get(workspaceId), {
    suspense: true,
  });
}

export const WorkspaceServiceProvider: React.FC = ({ children }) => {
  const user = useCurrentUser();
  const [currentWorkspaceId, setCurrentWorkspaceId] = useLocalStorage<
    string | null
  >(`${user.userId}/workspaceId`, null);
  const createWorkspace = useCreateWorkspace();
  const removeWorkspace = useRemoveWorkspace();

  const queryClient = useQueryClient();
  const resetCache = useResetter();

  const ctx = useMemo<Context>(
    () => ({
      currentWorkspaceId,
      createWorkspace: async (name: string) =>
        await createWorkspace({
          name,
          userId: user.userId,
        }),
      removeWorkspace,
      selectWorkspace: async (workspaceId) => {
        setCurrentWorkspaceId(workspaceId);
        await queryClient.resetQueries();
        resetCache();
      },
    }),
    [currentWorkspaceId, user, createWorkspace, removeWorkspace]
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
