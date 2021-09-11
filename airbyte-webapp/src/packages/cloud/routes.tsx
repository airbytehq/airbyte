import React, { Suspense, useMemo } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";
import { FormattedMessage } from "react-intl";
import { useAsync } from "react-use";

import SourcesPage from "pages/SourcesPage";
import DestinationPage from "pages/DestinationPage";
import {
  DestinationsPage as SettingsDestinationPage,
  SourcesPage as SettingsSourcesPage,
} from "pages/SettingsPage/pages/ConnectorsPage";
import ConnectionPage from "pages/ConnectionPage";
import SettingsPage from "pages/SettingsPage";
import ConfigurationsPage from "pages/SettingsPage/pages/ConfigurationsPage";
import NotificationPage from "pages/SettingsPage/pages/NotificationPage";

import LoadingPage from "components/LoadingPage";
import MainView from "packages/cloud/views/layout/MainView";
import { WorkspacesPage } from "packages/cloud/views/workspaces";
import { useApiHealthPoll } from "hooks/services/Health";
import { Auth } from "packages/cloud/views/auth";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import useConnector from "hooks/services/useConnector";

import {
  useGetWorkspace,
  useWorkspaceService,
  WorkspaceServiceProvider,
} from "packages/cloud/services/workspaces/WorkspacesService";
import { PageConfig } from "pages/SettingsPage/SettingsPage";
import { WorkspaceSettingsView } from "./views/workspaces/WorkspaceSettingsView";
import { UsersSettingsView } from "packages/cloud/views/users/UsersSettingsView/UsersSettingsView";
import { AccountSettingsView } from "packages/cloud/views/users/AccountSettingsView/AccountSettingsView";
import { ConfirmEmailPage } from "./views/auth/ConfirmEmailPage";
import useRouter from "hooks/useRouter";
import { WithPageAnalytics } from "pages/withPageAnalytics";

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
  Root = "/",
  SelectWorkspace = "/workspaces",
  Configuration = "/configuration",
  AccessManagement = "/access-management",
  Notifications = "/notifications",

  // Auth routes
  Signup = "/signup",
  Login = "/login",
  ResetPassword = "/reset-password",
  ConfirmPasswordReset = "/confirm-password-reset",
  VerifyEmail = "/verify-email",
  ConfirmVerifyEmail = "/confirm-verify-email",
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
  useApiHealthPoll();
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

const VerifyEmailRoute: React.FC = () => {
  const { query } = useRouter<{ oobCode: string }>();
  const { verifyEmail } = useAuthService();

  useAsync(async () => await verifyEmail(query.oobCode), []);

  return <LoadingPage />;
};

export const Routing: React.FC = () => {
  const { user, inited, emailVerified } = useAuthService();

  return (
    <Router>
      <WithPageAnalytics />
      <Suspense fallback={<LoadingPage />}>
        {inited ? (
          <>
            {user && emailVerified && (
              <WorkspaceServiceProvider>
                <MainViewRoutes />
              </WorkspaceServiceProvider>
            )}
            {user && !emailVerified && (
              <Switch>
                <Route path={Routes.VerifyEmail}>
                  <VerifyEmailRoute />
                </Route>
                <Route path={Routes.ConfirmVerifyEmail}>
                  <ConfirmEmailPage />
                </Route>
                <Redirect to={Routes.ConfirmVerifyEmail} />
              </Switch>
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
