import React, { useMemo } from "react";
import { useIntl } from "react-intl";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

import { useConfig } from "config";
import { Workspace } from "core/domain/workspace/Workspace";
import { TrackPageAnalytics, useAnalyticsIdentifyUser, useAnalyticsRegisterValues } from "hooks/services/Analytics";
import { useApiHealthPoll } from "hooks/services/Health";
import { useNotificationService } from "hooks/services/Notification";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useListWorkspaces } from "services/workspaces/WorkspacesService";
import { storeUtmFromQuery } from "utils/utmStorage";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import MainView from "views/layout/MainView";

import ConnectionPage from "./ConnectionPage";
import DestinationPage from "./DestinationPage";
import OnboardingPage from "./OnboardingPage";
import PreferencesPage from "./PreferencesPage";
import { RoutePaths } from "./routePaths";
import SettingsPage from "./SettingsPage";
import SourcesPage from "./SourcesPage";

function useDemo() {
  const { formatMessage } = useIntl();
  const config = useConfig();

  const demoNotification = useMemo(
    () => ({
      id: "demo.message",
      title: formatMessage({ id: "demo.message.title" }),
      text: formatMessage({ id: "demo.message.body" }),
      nonClosable: true,
    }),
    [formatMessage]
  );

  useNotificationService(config.isDemo ? demoNotification : undefined);
}

const useAddAnalyticsContextForWorkspace = (workspace: Workspace): void => {
  const analyticsContext = useMemo(
    () => ({
      workspace_id: workspace.workspaceId,
      customer_id: workspace.customerId,
    }),
    [workspace.workspaceId, workspace.customerId]
  );
  useAnalyticsRegisterValues(analyticsContext);
  useAnalyticsIdentifyUser(workspace.workspaceId);
};

const MainViewRoutes: React.FC<{ workspace: Workspace }> = ({ workspace }) => {
  return (
    <MainView>
      <TrackPageAnalytics />
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
      replace={true}
    />
  );
};

const RoutingWithWorkspace: React.FC = () => {
  const workspace = useCurrentWorkspace();
  useAddAnalyticsContextForWorkspace(workspace);
  useApiHealthPoll();
  useDemo();

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
