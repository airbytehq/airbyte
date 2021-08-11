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
import {
  SourcesPage as SettingsSourcesPage,
  DestinationsPage as SettingsDestinationPage,
} from "pages/SettingsPage/pages/ConnectorsPage";
import ConnectionPage from "pages/ConnectionPage";
import SettingsPage from "pages/SettingsPage";
import ConfigurationsPage from "pages/SettingsPage/pages/ConfigurationsPage";
import NotificationPage from "pages/SettingsPage/pages/NotificationPage";

import LoadingPage from "components/LoadingPage";
import MainView from "packages/cloud/views/layout/MainView";
import { WorkspacesPage } from "packages/cloud/views/workspaces";
import { useApiHealthPoll } from "components/hooks/services/Health";
import { Auth } from "packages/cloud/views/auth";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import useConnector from "components/hooks/services/useConnector";

import {
  useGetWorkspace,
  useWorkspaceService,
  WorkspaceServiceProvider,
} from "packages/cloud/services/workspaces/WorkspacesService";
import { HealthService } from "core/health/HealthService";
import { useDefaultRequestMiddlewares } from "./services/useDefaultRequestMiddlewares";
import { PageConfig } from "pages/SettingsPage/SettingsPage";
import { WorkspaceSettingsView } from "./views/workspaces/WorkspaceSettingsView";
import { UsersSettingsView } from "packages/cloud/views/users/UsersSettingsView/UsersSettingsView";
import { AccountSettingsView } from "packages/cloud/views/users/AccountSettingsView/AccountSettingsView";

export enum Routes {
  Preferences = "/preferences",
  Onboarding = "/onboarding",

  Connections = "/connections",
  Destination = "/destination",
  Source = "/source",
  Workspace = "/workspaces",
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
  AccessManagement = "/access-management",
  Notifications = "/notifications",
}

const MainRoutes: React.FC<{ currentWorkspaceId: string }> = ({
  currentWorkspaceId,
}) => {
  useGetWorkspace(currentWorkspaceId);
  const { countNewSourceVersion, countNewDestinationVersion } = useConnector();

  const pageConfig = useMemo<PageConfig>(
    () => ({
      menuConfig: [
        {
          category: <FormattedMessage id="settings.userSettings" />,
          routes: [
            {
              path: `${Routes.Settings}${Routes.Account}`,
              name: <FormattedMessage id="settings.account" />,
              component: AccountSettingsView,
            },
          ],
        },
        {
          category: <FormattedMessage id="settings.workspaceSettings" />,
          routes: [
            {
              path: `${Routes.Settings}${Routes.Workspace}`,
              name: <FormattedMessage id="settings.generalSettings" />,
              component: WorkspaceSettingsView,
            },
            {
              path: `${Routes.Settings}${Routes.Source}`,
              name: <FormattedMessage id="tables.sources" />,
              indicatorCount: countNewSourceVersion,
              component: SettingsSourcesPage,
            },
            {
              path: `${Routes.Settings}${Routes.Destination}`,
              name: <FormattedMessage id="tables.destinations" />,
              indicatorCount: countNewDestinationVersion,
              component: SettingsDestinationPage,
            },
            {
              path: `${Routes.Settings}${Routes.Configuration}`,
              name: <FormattedMessage id="admin.configuration" />,
              component: ConfigurationsPage,
            },
            {
              path: `${Routes.Settings}${Routes.AccessManagement}`,
              name: <FormattedMessage id="settings.accessManagementSettings" />,
              component: UsersSettingsView,
            },
            {
              path: `${Routes.Settings}${Routes.Notifications}`,
              name: <FormattedMessage id="settings.notifications" />,
              component: NotificationPage,
            },
          ],
        },
      ],
    }),
    [countNewSourceVersion, countNewDestinationVersion]
  );

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
        <SettingsPage pageConfig={pageConfig} />
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
