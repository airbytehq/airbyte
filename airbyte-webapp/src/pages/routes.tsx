import React, { Suspense, useEffect, useMemo } from "react";
import { Redirect, Route, Switch } from "react-router-dom";
import { useIntl } from "react-intl";

import { useConfig } from "config";

import SourcesPage from "./SourcesPage";
import DestinationPage from "./DestinationPage";
import PreferencesPage from "./PreferencesPage";
import OnboardingPage from "./OnboardingPage";
import ConnectionPage from "./ConnectionPage";
import SettingsPage from "./SettingsPage";
import LoadingPage from "components/LoadingPage";
import MainView from "views/layout/MainView";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";

import { useNotificationService } from "hooks/services/Notification";
import { useApiHealthPoll } from "hooks/services/Health";
import {
  TrackPageAnalytics,
  useAnalyticsIdentifyUser,
  useAnalyticsRegisterValues,
} from "hooks/services/Analytics";
import { Workspace } from "core/resources/Workspace";
import {
  useListWorkspaces,
  useWorkspaceService,
} from "../services/workspaces/WorkspacesService";
import { OnboardingServiceProvider } from "../hooks/services/Onboarding";
import useRouter from "../hooks/useRouter";

export enum Routes {
  Preferences = "/preferences",
  Onboarding = "/onboarding",

  Connections = "/connections",
  Destination = "/destination",
  Source = "/source",
  Connection = "/connection",
  ConnectionNew = "/new-connection",
  SourceNew = "/new-source",
  DestinationNew = "/new-destination",
  Settings = "/settings",
  Configuration = "/configuration",
  Notifications = "/notifications",
  Metrics = "/metrics",
  Account = "/account",
  AuthFlow = "/auth_flow",
  Root = "/",
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

const MainViewRoutes: React.FC<{ workspace: Workspace }> = ({ workspace }) => (
  <MainView>
    <Suspense fallback={<LoadingPage />}>
      <Switch>
        <Route path={Routes.AuthFlow}>
          <CompleteOauthRequest />
        </Route>
        <Route path={Routes.Destination}>
          <DestinationPage />
        </Route>
        <Route path={Routes.Source}>
          <SourcesPage />
        </Route>
        <Route path={Routes.Connections}>
          <ConnectionPage />
        </Route>
        <Route path={Routes.Settings}>
          <SettingsPage />
        </Route>
        {workspace.displaySetupWizard && (
          <Route path={Routes.Onboarding}>
            <OnboardingPage />
          </Route>
        )}
        <Redirect
          to={
            workspace.displaySetupWizard
              ? Routes.Onboarding
              : Routes.Connections
          }
        />
      </Switch>
    </Suspense>
  </MainView>
);

const PreferencesRoutes = () => (
  <Switch>
    <Route path={Routes.Preferences}>
      <PreferencesPage />
    </Route>
    <Redirect to={Routes.Preferences} />
  </Switch>
);

export const useAutoSelectFirstWorkspace = (): Workspace => {
  const workspaces = useListWorkspaces();

  const currentWorkspace = workspaces[0];

  const { selectWorkspace } = useWorkspaceService();

  const { pathname } = useRouter();
  const currentPath = pathname.split("/");
  const currentWorkspaceId =
    currentPath[0] === "workspace" ? currentPath[1] : null;

  console.log(currentWorkspaceId);

  useEffect(() => selectWorkspace(currentWorkspace.workspaceId), [
    currentWorkspace.workspaceId,
  ]);

  return workspaces[0];
};

export const Routing: React.FC = () => {
  const workspace = useAutoSelectFirstWorkspace();

  useAddAnalyticsContextForWorkspace(workspace);
  useApiHealthPoll();
  useDemo();

  return (
    <Suspense fallback={<LoadingPage />}>
      <OnboardingServiceProvider>
        {!workspace.initialSetupComplete ? (
          <PreferencesRoutes />
        ) : (
          <>
            <TrackPageAnalytics />
            <MainViewRoutes workspace={workspace} />
          </>
        )}
      </OnboardingServiceProvider>
    </Suspense>
  );
};
