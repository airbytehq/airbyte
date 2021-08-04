import React, { useContext, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "react-query";

import { CloudWorkspacesService } from "packages/cloud/lib/domain/cloudWorkspaces/CloudWorkspacesService";
import { RequestAuthMiddleware } from "packages/cloud/lib/auth/RequestAuthMiddleware";
import { api } from "packages/cloud/config/api";
import { useRequestMiddlewareProvider } from "core/request/useRequestMiddlewareProvider";
import { RequestMiddleware } from "core/request/RequestMiddleware";
import { jwtProvider } from "packages/cloud/services/auth/JwtProvider";

type Context = {
  currentWorkspaceId?: string;
  selectWorkspace: (workspaceId: string) => void;
  createWorkspace: (name: string) => void;
};

const defaultState: Context = {
  createWorkspace: (_: string) => ({}),
  selectWorkspace: (_: string) => ({}),
};

export const WorkspaceServiceContext = React.createContext<Context>(
  defaultState
);

export const useDefaultRequestMiddlewares = (): RequestMiddleware[] => {
  const requestAuthMiddleware = useMemo(
    () => RequestAuthMiddleware(jwtProvider),
    []
  );

  const { register, unregister } = useRequestMiddlewareProvider();

  // This is done only to allow injecting middlewares for static fields of BaseResource
  useEffect(() => {
    register("AuthMiddleware", requestAuthMiddleware);

    return () => unregister("AuthMiddleware");
  }, [register, unregister, requestAuthMiddleware]);

  return useMemo(() => [requestAuthMiddleware], [requestAuthMiddleware]);
};

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
  const service = useGetWorkspaceService();

  return useMutation(service.create.bind(service)).mutate;
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
  const ctx: Context = useMemo(
    () => ({
      currentWorkspaceId,
      createWorkspace: async (name: string) => {
        await createWorkspace({ name });
      },
      selectWorkspace: setCurrentWorkspaceId,
    }),
    [currentWorkspaceId, createWorkspace]
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
