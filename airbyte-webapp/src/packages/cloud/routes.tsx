import React, { Suspense, useEffect, useMemo } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";
import { FormattedMessage } from "react-intl";
import { useAsync } from "react-use";
import { useIntercom } from "react-use-intercom";

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
import OnboardingPage from "pages/OnboardingPage";
import { CreditsPage } from "packages/cloud/views/credits";
import { ConfirmEmailPage } from "./views/auth/ConfirmEmailPage";
import useRouter from "hooks/useRouter";
import { WithPageAnalytics } from "pages/withPageAnalytics";
import useWorkspace from "../../hooks/services/useWorkspace";
import { CompleteOauthRequest } from "../../pages/CompleteOauthRequest";

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
  AuthFlow = "/auth_flow",
  Root = "/",
  SelectWorkspace = "/workspaces",
  Configuration = "/configuration",
  AccessManagement = "/access-management",
  Notifications = "/notifications",
  Credits = "/credits",

  // Auth routes
  Signup = "/signup",
  Login = "/login",
  ResetPassword = "/reset-password",
  ConfirmVerifyEmail = "/confirm-verify-email",

  // Firebase action routes
  // These URLs come from Firebase emails, and all have the same
  // action URL ("/verify-email") with different "mode" parameter
  // TODO: use a better action URL in Firebase email template
  FirebaseAction = "/verify-email",
}

export enum FirebaseActionMode {
  VERIFY_EMAIL = "verifyEmail",
  RESET_PASSWORD = "resetPassword",
}

const MainRoutes: React.FC<{ currentWorkspaceId: string }> = ({
  currentWorkspaceId,
}) => {
  useGetWorkspace(currentWorkspaceId);
  const { countNewSourceVersion, countNewDestinationVersion } = useConnector();
  const { workspace } = useWorkspace();
  const mainRedirect = workspace.displaySetupWizard
    ? Routes.Onboarding
    : Routes.Connections;

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
      <Route path={Routes.Credits}>
        <CreditsPage />
      </Route>
      {workspace.displaySetupWizard && (
        <Route exact path={Routes.Onboarding}>
          <OnboardingPage />
        </Route>
      )}
      <Redirect to={mainRedirect} />
    </Switch>
  );
};

const MainViewRoutes = () => {
  useApiHealthPoll();
  const { currentWorkspaceId } = useWorkspaceService();

  return (
    <>
      <Switch>
        <Route path={Routes.AuthFlow}>
          <CompleteOauthRequest />
        </Route>
        <Route>
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
        </Route>
      </Switch>
    </>
  );
};

const FirebaseActionRoute: React.FC = () => {
  const { query } = useRouter<{ oobCode: string }>();
  const { verifyEmail } = useAuthService();

  useAsync(async () => await verifyEmail(query.oobCode), []);

  return <LoadingPage />;
};

export const Routing: React.FC = () => {
  const { user, inited, emailVerified } = useAuthService();

  const { boot } = useIntercom();

  useEffect(() => {
    if (user && user.email && user.name) {
      boot({
        email: user.email,
        name: user.name,
      });
    }
  }, [user]);

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
                <Route path={Routes.FirebaseAction}>
                  <FirebaseActionRoute />
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
