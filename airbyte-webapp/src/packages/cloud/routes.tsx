import React, { Suspense } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";

import config from "config";

import SourcesPage from "pages/SourcesPage";
import DestinationPage from "pages/DestinationPage";
import ConnectionPage from "pages/ConnectionPage";
import SettingsPage from "pages/SettingsPage";
import LoadingPage from "components/LoadingPage";
import MainView from "components/MainView";
import { useApiHealthPoll } from "components/hooks/services/Health";
import { Auth } from "./views/auth";
import { useAuthService } from "./services/auth/AuthService";

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

const MainViewRoutes = () => {
  useApiHealthPoll(config.healthCheckInterval);

  return (
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
          <Redirect to={Routes.Connections} />
        </Switch>
      </Suspense>
    </MainView>
  );
};

export const Routing: React.FC = () => {
  const { user, inited } = useAuthService();
  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        {inited ? (
          <>
            {user && <MainViewRoutes />}
            {!user && <Auth />}
          </>
        ) : (
          <LoadingPage />
        )}
      </Suspense>
    </Router>
  );
};
