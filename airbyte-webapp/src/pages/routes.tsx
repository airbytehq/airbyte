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
import AdminPage from "./AdminPage";
import LoadingPage from "../components/LoadingPage";
import MainView from "../components/MainView";
import config from "../config";
import WorkspaceResource from "../core/resources/Workspace";
import useSegment from "../components/hooks/useSegment";
import { AnalyticsService } from "../core/analytics/AnalyticsService";
import useRouter from "../components/hooks/useRouterHook";

export enum Routes {
  Preferences = "/preferences",
  Onboarding = "/onboarding",

  Destination = "/destination",
  Source = "/source",
  Connection = "/connection",
  SourceNew = "/new-source",
  Admin = "/admin",
  Root = "/"
}

const getPageName = (pathname: string) => {
  const itemPageRegex = new RegExp(`${Routes.Source}/.*`);

  if (pathname === Routes.Destination) {
    return "Destination Page";
  }
  if (pathname === Routes.Root) {
    return "Sources Page";
  }
  if (pathname === `${Routes.Source}${Routes.SourceNew}`) {
    return "Create Source Page";
  }
  if (pathname.match(itemPageRegex)) {
    return "Source Item Page";
  }
  if (pathname === Routes.Admin) {
    return "Admin Page";
  }

  return "";
};

const MainViewRoutes = () => {
  const { pathname } = useRouter();
  useEffect(() => {
    const pageName = getPageName(pathname);
    if (pageName) {
      AnalyticsService.page(pageName);
    }
  }, [pathname]);

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
          <Route path={Routes.Admin}>
            <AdminPage />
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

  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        {!workspace.initialSetupComplete ? (
          <PreferencesRoutes />
        ) : !workspace.onboardingComplete ? (
          <OnboardingsRoutes />
        ) : (
          <MainViewRoutes />
        )}
      </Suspense>
    </Router>
  );
};
