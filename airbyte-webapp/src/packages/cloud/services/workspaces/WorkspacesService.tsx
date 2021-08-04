import React, { useContext, useMemo, useState } from "react";
import { useMutation, useQuery } from "react-query";

import { CloudWorkspacesService } from "packages/cloud/lib/domain/cloudWorkspaces/CloudWorkspacesService";
import { api } from "packages/cloud/config/api";
import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useDefaultRequestMiddlewares } from "packages/cloud/services/useDefaultRequestMiddlewares";
import { WorkspaceService } from "packages/cloud/lib/domain/cloudWorkspaces/WorkspaceService";

type Context = {
  currentWorkspaceId?: string;
  selectWorkspace: (workspaceId: string) => void;
  createWorkspace: (name: string) => Promise<void>;
};

const defaultState: Context = {
  createWorkspace: async (_: string) => {
    throw new Error("createWorkspace was not specified");
  },
  selectWorkspace: (_: string) => ({}),
};

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

  return useQuery("workspaces", service.list.bind(service), {
    suspense: true,
  });
}

export function useCreateWorkspace() {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  const service = useGetWorkspaceService();

  return useMutation(
    async (payload: { name: string; billingUsedId: string }) => {
      // TODO: temp workaround for https://github.com/airbytehq/airbyte/issues/5191
      const workspaceService = new WorkspaceService(requestAuthMiddleware);
      const workspace = await workspaceService.create({ name: payload.name });

      return service.create({ ...payload, workspaceId: workspace.workspaceId });
    }
  ).mutate;
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
  const user = useCurrentUser();

  const ctx: Context = useMemo(
    () => ({
      currentWorkspaceId,
      createWorkspace: async (name: string) => {
        await createWorkspace({
          name,
          billingUsedId: user.userId,
        });
      },
      selectWorkspace: setCurrentWorkspaceId,
    }),
    [currentWorkspaceId, user, createWorkspace]
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
