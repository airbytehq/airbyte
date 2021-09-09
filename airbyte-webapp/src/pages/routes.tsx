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
import SupportChat from "components/SupportChat";

import { useWorkspace } from "hooks/services/useWorkspace";
import { useNotificationService } from "hooks/services/Notification/NotificationService";
import { useApiHealthPoll } from "hooks/services/Health";
import { WithPageAnalytics } from "./withPageAnalytics";

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
  Root = "/",
}

const MainViewRoutes = () => (
  <MainView>
    <Suspense fallback={<LoadingPage />}>
      <Switch>
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
        <Route exact path={Routes.Root}>
          <SourcesPage />
        </Route>
        <Redirect to={Routes.Root} />
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

const OnboardingsRoutes = () => (
  <Switch>
    <Route path={Routes.Onboarding}>
      <OnboardingPage />
    </Route>
    <Redirect to={Routes.Onboarding} />
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
  const config = useConfig();

  useApiHealthPoll();
  useDemo();

  const { workspace } = useWorkspace();

  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        {!workspace.initialSetupComplete ? (
          <PreferencesRoutes />
        ) : workspace.displaySetupWizard ? (
          <OnboardingsRoutes />
        ) : (
          <>
            <WithPageAnalytics />
            <MainViewRoutes />
          </>
        )}
        <SupportChat
          papercupsConfig={config.papercups}
          customerId={workspace.customerId}
          onClick={() => window.open(config.ui.slackLink, "_blank")}
        />
      </Suspense>
    </Router>
  );
};
