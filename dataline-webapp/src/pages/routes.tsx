import React, { Suspense } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch
} from "react-router-dom";

import SourcesPage from "./SourcesPage";
import DestinationPage from "./DestinationPage";
import PreferencesPage from "./PreferencesPage";
import OnboardingPage from "./OnboardingPage";
import LoadingPage from "../components/LoadingPage";
import MainView from "../components/MainView";

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

export const Routing = () => {
  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        <Switch>
          <Route path={Routes.Preferences}>
            <PreferencesPage />
          </Route>
          <Route path={Routes.Onboarding}>
            <OnboardingPage />
          </Route>
          <MainViewRoutes />

          <Redirect to={Routes.Root} />
        </Switch>
      </Suspense>
    </Router>
  );
};
