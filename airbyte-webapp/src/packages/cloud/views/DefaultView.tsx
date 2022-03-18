import { LoadingPage } from "components";
import { Navigate } from "react-router-dom";
import { CloudRoutes } from "../cloudRoutes";
import {
  useListCloudWorkspaces,
  useWorkspaceService,
} from "../services/workspaces/WorkspacesService";

export const DefaultView: React.FC = () => {
  const workspaces = useListCloudWorkspaces();
  const { selectWorkspace } = useWorkspaceService();

  // Only show the workspace creation list if there is more than one workspace
  if (workspaces.length > 1) {
    return <Navigate to={`/${CloudRoutes.SelectWorkspace}`} replace />;
  }

  // Otherwise directly switch to the single workspace
  selectWorkspace(workspaces[0].workspaceId);

  return <LoadingPage />;
};
