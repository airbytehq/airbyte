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
import LoadingPage from "../components/LoadingPage";
import MainView from "../components/MainView";

export enum Routes {
  Preferences = "/preferences",

  Destination = "/destination",
  Root = "/"
}

const MainViewRoutes = () => {
  return (
    <Switch>
      <MainView>
        <Suspense fallback={<LoadingPage />}>
          <Route exact path={Routes.Destination}>
            <DestinationPage />
          </Route>
          <Route exact path={Routes.Root}>
            <SourcesPage />
          </Route>
          <Redirect to={Routes.Root} />
        </Suspense>
      </MainView>
    </Switch>
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
          <MainViewRoutes />

          <Redirect to={Routes.Root} />
        </Switch>
      </Suspense>
    </Router>
  );
};
