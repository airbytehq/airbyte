import React, { useCallback, useContext, useMemo } from "react";
import { useQueryClient } from "react-query";
import { useResetter, useResource } from "rest-hooks";

import WorkspaceResource from "core/resources/Workspace";
import useRouter from "hooks/useRouter";
import { Workspace } from "core/domain/workspace/Workspace";
import { RoutePaths } from "pages/routes";

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
  const resetCache = useResetter();
  const { push } = useRouter();

  return useCallback(
    async (workspace) => {
      if (typeof workspace === "object") {
        push(`/${RoutePaths.Workspaces}/${workspace?.workspaceId}`);
      } else {
        push(`/${RoutePaths.Workspaces}/${workspace}`);
      }
      await queryClient.resetQueries();
      resetCache();
    },
    [push, queryClient, resetCache]
  );
};

export const WorkspaceServiceProvider: React.FC = ({ children }) => {
  const selectWorkspace = useSelectWorkspace();

  const ctx = useMemo<Context>(
    () => ({
      selectWorkspace,
      exitWorkspace: () => selectWorkspace(""),
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

export const useCurrentWorkspace = (): Workspace => {
  const { params } = useRouter<unknown, { workspaceId: string }>();
  const { workspaceId } = params;

  return useResource(WorkspaceResource.detailShape(), {
    workspaceId: workspaceId,
  });
};

export const useListWorkspaces = (): Workspace[] => {
  return useResource(WorkspaceResource.listShape(), {}).workspaces;
};
