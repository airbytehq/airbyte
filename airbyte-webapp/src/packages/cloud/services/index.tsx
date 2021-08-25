import { useResource } from "rest-hooks";
import { registerService } from "core/servicesProvider";
import { useWorkspaceService } from "./workspaces/WorkspacesService";
import { useAuthService } from "./auth/AuthService";
import WorkspaceResource from "core/resources/Workspace";

export const useCustomerIdProvider = () => {
  const { user } = useAuthService();
  return user?.userId ?? "";
};

registerService("currentWorkspaceProvider", () => {
  const { currentWorkspaceId } = useWorkspaceService();
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: currentWorkspaceId || null,
  });

  return workspace;
});
