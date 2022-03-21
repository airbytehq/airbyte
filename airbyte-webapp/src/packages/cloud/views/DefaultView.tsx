import { RoutePaths } from "pages/routes";
import { Navigate } from "react-router-dom";
import { CloudRoutes } from "../cloudRoutes";
import { useListCloudWorkspaces } from "../services/workspaces/WorkspacesService";

export const DefaultView: React.FC = () => {
  const workspaces = useListCloudWorkspaces();

  // Only show the workspace creation list if there is more than one workspace
  if (workspaces.length > 1) {
    return <Navigate to={`/${CloudRoutes.SelectWorkspace}`} replace />;
  }

  return (
    <Navigate
      to={`/${RoutePaths.Workspaces}/${workspaces[0].workspaceId}`}
      replace
    />
  );
};
