import React, { Suspense, useEffect } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch
} from "react-router-dom";
import { useResource } from "rest-hooks";
import ChatWidget from "@papercups-io/chat-widget";
import { Storytime } from "@papercups-io/storytime";

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
  ConnectionNew = "/new-connection",
  SourceNew = "/new-source",
  DestinationNew = "/new-destination",
  Admin = "/admin",
  Root = "/"
}

const getPageName = (pathname: string) => {
  const itemSourcePageRegex = new RegExp(`${Routes.Source}/.*`);
  const itemDestinationPageRegex = new RegExp(`${Routes.Destination}/.*`);
  const itemSourceToDestinationPageRegex = new RegExp(
    `(${Routes.Source}|${Routes.Destination})${Routes.Connection}/.*`
  );

  if (pathname === Routes.Destination) {
    return "Destinations Page";
  }
  if (pathname === Routes.Root) {
    return "Sources Page";
  }
  if (pathname === `${Routes.Source}${Routes.SourceNew}`) {
    return "Create Source Page";
  }
  if (pathname === `${Routes.Destination}${Routes.DestinationNew}`) {
    return "Create Destination Page";
  }
  if (
    pathname === `${Routes.Source}${Routes.ConnectionNew}` ||
    pathname === `${Routes.Destination}${Routes.ConnectionNew}`
  ) {
    return "Create Connection Page";
  }
  if (pathname.match(itemSourceToDestinationPageRegex)) {
    return "Source to Destination Page";
  }
  if (pathname.match(itemDestinationPageRegex)) {
    return "Destination Item Page";
  }
  if (pathname.match(itemSourcePageRegex)) {
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

  useEffect(() => {
    if (workspace) {
      AnalyticsService.identify(workspace.customerId);
    }
  }, [workspace]);

  const customer = {
    external_id: workspace.customerId
  };
  Storytime.init({
    accountId: "74560291-451e-4ceb-a802-56706ece528b",
    customer,
    baseUrl: "https://app.papercups.io"
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
        <ChatWidget
          title="Welcome to Airbyte"
          subtitle="Ask us anything in the chat window below 😊"
          primaryColor="#625eff"
          greeting="Hello!!!"
          newMessagePlaceholder="Start typing..."
          customer={customer}
          accountId="74560291-451e-4ceb-a802-56706ece528b"
          baseUrl="https://app.papercups.io"
        />
      </Suspense>
    </Router>
  );
};
