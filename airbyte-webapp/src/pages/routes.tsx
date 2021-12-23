import React, { useMemo } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useIntl } from "react-intl";
import { useLocation } from "react-use";

import { useConfig } from "config";

import SourcesPage from "./SourcesPage";
import DestinationPage from "./DestinationPage";
import PreferencesPage from "./PreferencesPage";
import OnboardingPage from "./OnboardingPage";
import ConnectionPage from "./ConnectionPage";
import SettingsPage from "./SettingsPage";
import MainView from "views/layout/MainView";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";

import { useNotificationService } from "hooks/services/Notification";
import { useApiHealthPoll } from "hooks/services/Health";
import {
  TrackPageAnalytics,
  useAnalyticsIdentifyUser,
  useAnalyticsRegisterValues,
} from "hooks/services/Analytics";
import { useListWorkspaces } from "services/workspaces/WorkspacesService";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { Workspace } from "core/domain/workspace/Workspace";

export enum RoutePaths {
  AuthFlow = "/auth_flow",
  Root = "/",

  Workspaces = "workspaces",
  Preferences = "preferences",
  Onboarding = "onboarding",
  Connections = "connections",
  Destination = "destination",
  Source = "source",
  Settings = "settings",

  Connection = "connection",
  ConnectionNew = "new-connection",
  SourceNew = "new-source",
  DestinationNew = "new-destination",
}

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
        <Route
          path={`${RoutePaths.Destination}/*`}
          element={<DestinationPage />}
        />
        <Route path={`${RoutePaths.Source}/*`} element={<SourcesPage />} />
        <Route
          path={`${RoutePaths.Connections}/*`}
          element={<ConnectionPage />}
        />
        <Route path={`${RoutePaths.Settings}/*`} element={<SettingsPage />} />
        {workspace.displaySetupWizard ? (
          <Route
            path={`${RoutePaths.Onboarding}/*`}
            element={<OnboardingPage />}
          />
        ) : null}
        <Route
          path="*"
          element={
            <Navigate
              to={
                workspace.displaySetupWizard
                  ? RoutePaths.Onboarding
                  : RoutePaths.Connections
              }
            />
          }
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

export const AutoSelectFirstWorkspace: React.FC<{ includePath?: boolean }> = ({
  includePath,
}) => {
  const location = useLocation();
  const workspaces = useListWorkspaces();
  const currentWorkspace = workspaces[0];

  return (
    <Navigate
      to={`/${RoutePaths.Workspaces}/${currentWorkspace.workspaceId}${
        includePath ? location.pathname : ""
      }`}
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
      {workspace.initialSetupComplete ? (
        <MainViewRoutes workspace={workspace} />
      ) : (
        <PreferencesRoutes />
      )}
    </OnboardingServiceProvider>
  );
};

export const Routing: React.FC = () => {
  // TODO: Remove this after it is verified there are no problems with current routing
  const OldRoutes = useMemo(
    () =>
      Object.values(RoutePaths).map((r) => (
        <Route
          path={`${r}/*`}
          key={r}
          element={<AutoSelectFirstWorkspace includePath />}
        />
      )),
    []
  );
  return (
    <Routes>
      {OldRoutes}
      <Route path={RoutePaths.AuthFlow} element={<CompleteOauthRequest />} />
      <Route
        path={`${RoutePaths.Workspaces}/:workspaceId/*`}
        element={<RoutingWithWorkspace />}
      />
      <Route path="*" element={<AutoSelectFirstWorkspace />} />
    </Routes>
  );
};
