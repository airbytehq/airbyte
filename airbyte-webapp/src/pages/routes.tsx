import React, { Suspense, useEffect } from "react";
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
// import ConnectionResource from "../core/resources/Connection";
import DestinationResource from "../core/resources/Destination";
import useSegment from "../components/hooks/useSegment";
import { AnalyticsService } from "../core/analytics/AnalyticsService";
import useRouter from "../components/hooks/useRouterHook";

export enum Routes {
  Preferences = "/preferences",
  Onboarding = "/onboarding",

  Destination = "/destination",
  Source = "/source",
  SourceNew = "/new-source",
  Root = "/"
}

const MainViewRoutes = () => {
  const { pathname } = useRouter();
  useEffect(() => {
    const itemPageRegex = new RegExp(`${Routes.Source}/.*`);
    if (pathname === Routes.Destination) {
      AnalyticsService.page("Destination Page");
    } else if (pathname === Routes.Root) {
      AnalyticsService.page("Sources Page");
    } else if (pathname === `${Routes.Source}${Routes.SourceNew}`) {
      AnalyticsService.page("Create Source Page");
    } else if (pathname.match(itemPageRegex)) {
      AnalyticsService.page("Source Item Page");
    }
  }, [pathname]);

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
  useSegment(config.segment.token);

  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: config.ui.workspaceId
  });

  // const { connections } = useResource(ConnectionResource.listShape(), {
  //   workspaceId: config.ui.workspaceId
  // });
  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        {!workspace.initialSetupComplete ? (
          <PreferencesRoutes />
        ) : !destinations.length ? (
          <OnboardingsRoutes />
        ) : (
          <MainViewRoutes />
        )}
      </Suspense>
    </Router>
  );
};
