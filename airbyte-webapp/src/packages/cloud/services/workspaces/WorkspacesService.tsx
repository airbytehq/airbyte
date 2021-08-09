import React, { useContext, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";

import { CloudWorkspacesService } from "packages/cloud/lib/domain/cloudWorkspaces/CloudWorkspacesService";
import { api } from "packages/cloud/config/api";
import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useDefaultRequestMiddlewares } from "packages/cloud/services/useDefaultRequestMiddlewares";
import { CloudWorkspace } from "packages/cloud/lib/domain/cloudWorkspaces/types";

type Context = {
  currentWorkspaceId?: string;
  selectWorkspace: (workspaceId: string) => void;
  createWorkspace: (name: string) => Promise<void>;
  removeWorkspace: {
    mutate: (workspaceId: string) => void;
    isLoading: boolean;
  };
};

const defaultState: Context = {} as Context;

export const WorkspaceServiceContext = React.createContext<Context>(
  defaultState
);

function useGetWorkspaceService() {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useMemo(
    () => new CloudWorkspacesService(requestAuthMiddleware, api.cloud),
    [requestAuthMiddleware]
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
  ).mutate;
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
  const [currentWorkspaceId, setCurrentWorkspaceId] = useState("");
  const createWorkspace = useCreateWorkspace();
  const removeWorkspace = useRemoveWorkspace();
  const user = useCurrentUser();

  const ctx = useMemo<Context>(
    () => ({
      currentWorkspaceId,
      createWorkspace: async (name: string) =>
        await createWorkspace({
          name,
          userId: user.userId,
        }),
      removeWorkspace,
      selectWorkspace: setCurrentWorkspaceId,
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
