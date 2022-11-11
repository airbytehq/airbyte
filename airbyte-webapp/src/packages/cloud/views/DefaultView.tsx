import { useEffect } from "react";
import { Navigate } from "react-router-dom";

import { useExperiment } from "hooks/services/Experiment";

import { RoutePaths } from "../../../pages/routePaths";
import { CloudRoutes } from "../cloudRoutes";
import { EXP_SOURCE_SIGNUP_SELECTOR } from "../components/experiments/constants";
import { useListCloudWorkspaces } from "../services/workspaces/CloudWorkspacesService";

export const DefaultView: React.FC = () => {
  const workspaces = useListCloudWorkspaces();
  // exp-signup-selected-source-definition
  const isSignupSourceSelectorExperiment = useExperiment("authPage.signup.sourceSelector", false);
  const sourceDefinitionId = localStorage.getItem(EXP_SOURCE_SIGNUP_SELECTOR);

  useEffect(() => {
    localStorage.removeItem(EXP_SOURCE_SIGNUP_SELECTOR);
  }, []);
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
      // exp-signup-selected-source-definition
      {...(isSignupSourceSelectorExperiment && {
        state: { sourceDefinitionId },
        to: `/${RoutePaths.Workspaces}/${workspaces[0].workspaceId}/${RoutePaths.Connections}/${RoutePaths.ConnectionNew}`,
      })}
    />
  );
};
