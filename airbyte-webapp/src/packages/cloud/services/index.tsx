import { useResource } from "rest-hooks";
import { useWorkspaceService } from "./workspaces/WorkspacesService";
import { useAuthService } from "./auth/AuthService";
import WorkspaceResource, { Workspace } from "core/resources/Workspace";

export const useCustomerIdProvider = (): string => {
  const { user } = useAuthService();
  return user?.userId ?? "";
};

export const useCurrentWorkspaceProvider = (): Workspace => {
  const { currentWorkspaceId } = useWorkspaceService();
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: currentWorkspaceId || null,
  });

  return workspace;
};
