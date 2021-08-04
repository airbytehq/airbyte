import React, { Suspense, useMemo } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";
import { FormattedMessage } from "react-intl";

import config from "config";

import SourcesPage from "pages/SourcesPage";
import DestinationPage from "pages/DestinationPage";
import ConnectionPage from "pages/ConnectionPage";
import SettingsPage from "pages/SettingsPage";
import LoadingPage from "components/LoadingPage";
import MainView from "components/MainView";
import { WorkspacesPage } from "./views/workspaces";
import { useApiHealthPoll } from "components/hooks/services/Health";
import { Auth } from "./views/auth";
import { useAuthService } from "./services/auth/AuthService";
import useConnector from "../../components/hooks/services/useConnector";

import {
  useGetWorkspace,
  useWorkspaceService,
  WorkspaceServiceProvider,
} from "./services/workspaces/WorkspacesService";
import { HealthService } from "core/health/HealthService";
import { useDefaultRequestMiddlewares } from "./services/useDefaultRequestMiddlewares";

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
  Metrics = "/metrics",
  Account = "/account",
  Signup = "/signup",
  Login = "/login",
  ResetPassword = "/reset-password",
  Root = "/",
  SelectWorkspace = "/workspaces",
  Configuration = "/configuration",
  Notifications = "/notifications",
}

const MainRoutes: React.FC<{ currentWorkspaceId: string }> = ({
  currentWorkspaceId,
}) => {
  useGetWorkspace(currentWorkspaceId);
  const { countNewSourceVersion, countNewDestinationVersion } = useConnector();

  const menuItems = [
    {
      category: <FormattedMessage id="settings.userSettings" />,
      routes: [
        {
          id: `${Routes.Settings}${Routes.Account}`,
          name: <FormattedMessage id="settings.account" />,
        },
      ],
    },
    {
      category: <FormattedMessage id="settings.workspaceSettings" />,
      routes: [
        {
          id: `${Routes.Settings}${Routes.Source}`,
          name: <FormattedMessage id="tables.sources" />,
          indicatorCount: countNewSourceVersion,
        },
        {
          id: `${Routes.Settings}${Routes.Destination}`,
          name: <FormattedMessage id="tables.destinations" />,
          indicatorCount: countNewDestinationVersion,
        },
        {
          id: `${Routes.Settings}${Routes.Configuration}`,
          name: <FormattedMessage id="admin.configuration" />,
        },
        {
          id: `${Routes.Settings}${Routes.Notifications}`,
          name: <FormattedMessage id="settings.notifications" />,
        },
      ],
    },
  ];

  return (
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
        <SettingsPage pageConfig={{ menuConfig: menuItems }} />
      </Route>
      <Route exact path={Routes.Root}>
        <SourcesPage />
      </Route>
      <Redirect to={Routes.Connections} />
    </Switch>
  );
};

const MainViewRoutes = () => {
  const middlewares = useDefaultRequestMiddlewares();
  const healthService = useMemo(() => new HealthService(middlewares), [
    middlewares,
  ]);

  useApiHealthPoll(config.healthCheckInterval, healthService);
  const { currentWorkspaceId } = useWorkspaceService();

  return (
    <>
      {currentWorkspaceId ? (
        <MainView>
          <Suspense fallback={<LoadingPage />}>
            <MainRoutes currentWorkspaceId={currentWorkspaceId} />
          </Suspense>
        </MainView>
      ) : (
        <Switch>
          <Route exact path={Routes.SelectWorkspace}>
            <WorkspacesPage />
          </Route>
          <Redirect to={Routes.SelectWorkspace} />
        </Switch>
      )}
    </>
  );
};

export const Routing: React.FC = () => {
  const { user, inited } = useAuthService();
  return (
    <Router>
      <Suspense fallback={<LoadingPage />}>
        {inited ? (
          <>
            {user && (
              <WorkspaceServiceProvider>
                <MainViewRoutes />
              </WorkspaceServiceProvider>
            )}
            {!user && <Auth />}
          </>
        ) : (
          <LoadingPage />
        )}
      </Suspense>
    </Router>
  );
};
