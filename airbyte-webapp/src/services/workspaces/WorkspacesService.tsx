import React, { useContext, useMemo } from "react";
import { useQueryClient } from "react-query";
import { useResetter, useResource } from "rest-hooks";

import WorkspaceResource, { Workspace } from "core/resources/Workspace";
import useRouter from "hooks/useRouter";

type Context = {
  selectWorkspace: (workspaceId?: string | null) => void;
};

export const WorkspaceServiceContext = React.createContext<Context | null>(
  null
);

export const WorkspaceServiceProvider: React.FC = ({ children }) => {
  const queryClient = useQueryClient();
  const resetCache = useResetter();
  const { push } = useRouter();

  const ctx = useMemo<Context>(
    () => ({
      selectWorkspace: async (workspaceId) => {
        push(workspaceId ?? "/");
        await queryClient.resetQueries();
        resetCache();
      },
    }),
    [push]
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

export const useCurrentWorkspace = (): Workspace => {
  const { params } = useRouter<unknown, { workspaceId: string }>();
  const { workspaceId } = params;

  // @ts-ignore
  return useResource(
    WorkspaceResource.detailShape(),
    workspaceId
      ? {
          workspaceId: workspaceId,
        }
      : null
  );
};

export const useListWorkspaces = (): Workspace[] => {
  return useResource(WorkspaceResource.listShape(), {}).workspaces;
};
