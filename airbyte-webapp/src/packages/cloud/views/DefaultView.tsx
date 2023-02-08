import { Navigate } from "react-router-dom";

import { RoutePaths } from "../../../pages/routePaths";
import { CloudRoutes } from "../cloudRoutePaths";
import { useListCloudWorkspaces } from "../services/workspaces/CloudWorkspacesService";

export const DefaultView: React.FC = () => {
  const workspaces = useListCloudWorkspaces();

  // Only show the workspace creation list if there is more than one workspace
  // otherwise redirect to the single workspace
  return (
    <Navigate
      to={
        workspaces.length !== 1
          ? `/${CloudRoutes.SelectWorkspace}`
          : `/${RoutePaths.Workspaces}/${workspaces[0].workspaceId}`
      }
      replace
    />
  );
};

export default DefaultView;
