import React, { Suspense, useMemo } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";
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

import { useWorkspace } from "hooks/services/useWorkspace";
import { useNotificationService } from "hooks/services/Notification";
import { useApiHealthPoll } from "hooks/services/Health";
import {
  useAnalyticsIdentifyUser,
  useAnalyticsRegisterValues,
  TrackPageAnalytics,
} from "hooks/services/Analytics";

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

const MainViewRoutes = () => {
  const { workspace } = useWorkspace();
  const mainRedirect = workspace.displaySetupWizard
    ? Routes.Onboarding
    : Routes.Connections;

  return (
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
          <Route exact path={Routes.Source}>
            <SourcesPage />
          </Route>
          <Redirect to={mainRedirect} />
        </Switch>
      </Suspense>
    </MainView>
  );
};

const PreferencesRoutes = () => (
  <Switch>
    <Route path={Routes.Preferences}>
      <PreferencesPage />
    </Route>
    <Redirect to={Routes.Preferences} />
  </Switch>
);

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

export const Routing: React.FC = () => {
  useApiHealthPoll();
  useDemo();

  const { workspace } = useWorkspace();

  const analyticsContext = useMemo(
    () => ({
      workspaceId: workspace.workspaceId,
      customerId: workspace.customerId,
    }),
    [workspace.workspaceId, workspace.customerId]
  );
  useAnalyticsRegisterValues(analyticsContext);
  useAnalyticsIdentifyUser(workspace.workspaceId);

  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        {!workspace.initialSetupComplete ? (
          <PreferencesRoutes />
        ) : (
          <>
            <TrackPageAnalytics />
            <MainViewRoutes />
          </>
        )}
      </Suspense>
    </Router>
  );
};
