import React, { Suspense } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch
} from "react-router-dom";
import { useResource } from "rest-hooks";

import SourcesPage from "./SourcesPage";
import DestinationPage from "./DestinationPage";
import PreferencesPage from "./PreferencesPage";
import OnboardingPage from "./OnboardingPage";
import LoadingPage from "../components/LoadingPage";
import MainView from "../components/MainView";
import config from "../config";
import WorkspaceResource from "../core/resources/Workspace";
import ConnectionResource from "../core/resources/Connection";

export enum Routes {
  Preferences = "/preferences",
  Onboarding = "/onboarding",

  Destination = "/destination",
  Source = "/source",
  SourceNew = "/new-source",
  Root = "/"
}

const MainViewRoutes = () => {
  return (
    <MainView>
      <Suspense fallback={<LoadingPage />}>
        <Switch>
          <Route exact path={Routes.Destination}>
            <DestinationPage />
          </Route>
          <Route path={Routes.Source}>
            <SourcesPage />
          </Route>
          <Route exact path={Routes.Root}>
            <SourcesPage />
          </Route>
          <Redirect to={Routes.Root} />
        </Switch>
      </Suspense>
    </MainView>
  );
};

const PreferencesRoutes = () => {
  return (
    <Switch>
      <Route path={Routes.Preferences}>
        <PreferencesPage />
      </Route>
      <Redirect to={Routes.Preferences} />
    </Switch>
  );
};

const OnboardingsRoutes = () => {
  return (
    <Switch>
      <Route path={Routes.Onboarding}>
        <OnboardingPage />
      </Route>
      <Redirect to={Routes.Onboarding} />
    </Switch>
  );
};

export const Routing = () => {
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: config.ui.workspaceId
  });

  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        {!workspace.initialSetupComplete ? (
          <PreferencesRoutes />
        ) : !connections.length ? (
          <OnboardingsRoutes />
        ) : (
          <MainViewRoutes />
        )}
      </Suspense>
    </Router>
  );
};
