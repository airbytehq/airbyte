import React, { useMemo } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

import ApiErrorBoundary from "components/ApiErrorBoundary";

import { useAnalyticsIdentifyUser, useAnalyticsRegisterValues } from "hooks/services/Analytics";
import { useTrackPageAnalytics } from "hooks/services/Analytics/useTrackPageAnalytics";
import { useApiHealthPoll } from "hooks/services/Health";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useListWorkspaces } from "services/workspaces/WorkspacesService";
import { storeUtmFromQuery } from "utils/utmStorage";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import MainView from "views/layout/MainView";

import { WorkspaceRead } from "../core/request/AirbyteClient";
import ConnectionPage from "./ConnectionPage";
import DestinationPage from "./DestinationPage";
import OnboardingPage from "./OnboardingPage";
import PreferencesPage from "./PreferencesPage";
import { RoutePaths } from "./routePaths";
import SettingsPage from "./SettingsPage";
import SourcesPage from "./SourcesPage";

const useAddAnalyticsContextForWorkspace = (workspace: WorkspaceRead): void => {
  const analyticsContext = useMemo(
    () => ({
      workspace_id: workspace.workspaceId,
      customer_id: workspace.customerId,
    }),
    [workspace.workspaceId, workspace.customerId]
  );
  useAnalyticsRegisterValues(analyticsContext);
  useAnalyticsIdentifyUser(workspace.workspaceId);
  useTrackPageAnalytics();
};

const MainViewRoutes: React.FC<{ workspace: WorkspaceRead }> = ({ workspace }) => {
  return (
    <MainView>
      <ApiErrorBoundary>
        <Routes>
          <Route path={`${RoutePaths.Destination}/*`} element={<DestinationPage />} />
          <Route path={`${RoutePaths.Source}/*`} element={<SourcesPage />} />
          <Route path={`${RoutePaths.Connections}/*`} element={<ConnectionPage />} />
          <Route path={`${RoutePaths.Settings}/*`} element={<SettingsPage />} />
          {workspace.displaySetupWizard ? (
            <Route path={`${RoutePaths.Onboarding}/*`} element={<OnboardingPage />} />
          ) : null}
          <Route
            path="*"
            element={<Navigate to={workspace.displaySetupWizard ? RoutePaths.Onboarding : RoutePaths.Connections} />}
          />
        </Routes>
      </ApiErrorBoundary>
    </MainView>
  );
};

const PreferencesRoutes = () => (
  <Routes>
    <Route path={RoutePaths.Preferences} element={<PreferencesPage />} />
    <Route path="*" element={<Navigate to={RoutePaths.Preferences} />} />
  </Routes>
);

export const AutoSelectFirstWorkspace: React.FC<{ includePath?: boolean }> = ({ includePath }) => {
  const location = useLocation();
  const workspaces = useListWorkspaces();
  const currentWorkspace = workspaces[0];

  return (
    <Navigate
      to={`/${RoutePaths.Workspaces}/${currentWorkspace.workspaceId}${includePath ? location.pathname : ""}`}
      replace
    />
  );
};

const RoutingWithWorkspace: React.FC = () => {
  const workspace = useCurrentWorkspace();
  useAddAnalyticsContextForWorkspace(workspace);
  useTrackPageAnalytics();
  useApiHealthPoll();

  return (
    <OnboardingServiceProvider>
      {workspace.initialSetupComplete ? <MainViewRoutes workspace={workspace} /> : <PreferencesRoutes />}
    </OnboardingServiceProvider>
  );
};

export const Routing: React.FC = () => {
  const { search } = useLocation();

  useEffectOnce(() => {
    storeUtmFromQuery(search);
  });

  // TODO: Remove this after it is verified there are no problems with current routing
  const OldRoutes = useMemo(
    () =>
      Object.values(RoutePaths).map((r) => (
        <Route path={`${r}/*`} key={r} element={<AutoSelectFirstWorkspace includePath />} />
      )),
    []
  );
  return (
    <Routes>
      {OldRoutes}
      <Route path={RoutePaths.AuthFlow} element={<CompleteOauthRequest />} />
      <Route path={`${RoutePaths.Workspaces}/:workspaceId/*`} element={<RoutingWithWorkspace />} />
      <Route path="*" element={<AutoSelectFirstWorkspace />} />
    </Routes>
  );
};
