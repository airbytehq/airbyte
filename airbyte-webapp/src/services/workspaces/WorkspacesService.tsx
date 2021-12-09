import React, { useContext, useMemo, useState } from "react";
import { useQueryClient } from "react-query";
import { useResetter, useResource } from "rest-hooks";

import WorkspaceResource, { Workspace } from "core/resources/Workspace";
// import useRouter from "hooks/useRouter";

type Context = {
  currentWorkspaceId: string | null;
  selectWorkspace: (workspaceId: string | null) => void;
};

export const WorkspaceServiceContext = React.createContext<Context | null>(
  null
);

export const WorkspaceServiceProvider: React.FC = ({ children }) => {
  const queryClient = useQueryClient();
  const resetCache = useResetter();
  // const { push } = useRouter();
  const [currentWorkspaceId, setCurrentWorkspaceId] = useState<string | null>(
    null
  );

  const ctx = useMemo<Context>(
    () => ({
      currentWorkspaceId: currentWorkspaceId,
      selectWorkspace: async (workspaceId) => {
        setCurrentWorkspaceId(workspaceId);
        await queryClient.resetQueries();
        resetCache();
      },
    }),
    [currentWorkspaceId, currentWorkspaceId]
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
  const { currentWorkspaceId } = useWorkspaceService();

  // @ts-ignore
  return useResource(
    WorkspaceResource.detailShape(),
    currentWorkspaceId
      ? {
          workspaceId: currentWorkspaceId,
        }
      : undefined
  );
};

export const useListWorkspaces = (): Workspace[] => {
  return useResource(WorkspaceResource.listShape(), {}).workspaces;
};
