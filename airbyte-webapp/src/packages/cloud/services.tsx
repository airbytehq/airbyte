import { useAuthService } from "./services/auth/AuthService";
import { registerService } from "core/servicesProvider";
import {
  useGetWorkspace,
  useWorkspaceService,
} from "./services/workspaces/WorkspacesService";

export const useCustomerIdProvider = () => {
  const { user } = useAuthService();
  return user?.userId ?? "";
};

registerService("currentWorkspaceProvider", () => {
  const { currentWorkspaceId } = useWorkspaceService();
  const { data: workspace } = useGetWorkspace(currentWorkspaceId ?? "");

  return workspace;
});
