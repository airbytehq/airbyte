import React, { useContext, useEffect, useMemo } from "react";

import { CloudWorkspacesService } from "packages/cloud/lib/domain/cloudWorkspaces/CloudWorkspacesService";
import { RequestAuthMiddleware } from "packages/cloud/lib/request/RequestAuthMiddleware";
import { api } from "packages/cloud/config/api";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

type Context = {};

const defaultState: Context = {};

export const WorkspaceServiceContext = React.createContext<Context>(
  defaultState
);

export const WorkspaceServiceProvider: React.FC = ({ children }) => {
  const ctx: Context = useMemo(() => ({}), []);
  const { user } = useAuthService();

  const jwtProvider = useMemo(
    () => ({
      getValue: (): string => user?.token ?? "",
    }),
    [user?.token]
  );

  const workspaceService = useMemo(
    () =>
      new CloudWorkspacesService(RequestAuthMiddleware(jwtProvider), api.cloud),
    [jwtProvider]
  );

  useEffect(() => {
    if (user) {
      workspaceService.list();
    }
  }, [workspaceService]);

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
