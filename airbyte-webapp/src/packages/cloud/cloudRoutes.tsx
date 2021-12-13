import React, { Suspense, useMemo } from "react";
import {
  BrowserRouter as Router,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import SourcesPage from "pages/SourcesPage";
import DestinationPage from "pages/DestinationPage";
import ConnectionPage from "pages/ConnectionPage";

import LoadingPage from "components/LoadingPage";
import MainView from "packages/cloud/views/layout/MainView";
import { WorkspacesPage } from "packages/cloud/views/workspaces";
import { useApiHealthPoll } from "hooks/services/Health";
import { Auth } from "packages/cloud/views/auth";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useIntercom } from "packages/cloud/services/thirdParty/intercom/useIntercom";

import { useGetWorkspace } from "packages/cloud/services/workspaces/WorkspacesService";
import {
  useCurrentWorkspace,
  WorkspaceServiceProvider,
} from "services/workspaces/WorkspacesService";
import OnboardingPage from "pages/OnboardingPage";
import { CreditsPage } from "packages/cloud/views/credits";
import { ConfirmEmailPage } from "./views/auth/ConfirmEmailPage";
import { TrackPageAnalytics } from "hooks/services/Analytics/TrackPageAnalytics";
import useWorkspace from "hooks/services/useWorkspace";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
import { useConfig } from "./services/config";
import useFullStory from "./services/thirdParty/fullstory/useFullStory";
import {
  useAnalyticsIdentifyUser,
  useAnalyticsRegisterValues,
} from "hooks/services/Analytics/useAnalyticsService";
import { CloudSettingsPage } from "./views/CloudSettingsPage";
import { VerifyEmailAction } from "./views/FirebaseActionRoute";

export enum CloudRoutes {
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

const MainRoutes: React.FC<{ currentWorkspaceId: string }> = ({
  currentWorkspaceId,
}) => {
  useGetWorkspace(currentWorkspaceId);
  const { workspace } = useWorkspace();

  const analyticsContext = useMemo(
    () => ({
      workspace_id: workspace.workspaceId,
      customer_id: workspace.customerId,
    }),
    [workspace]
  );
  useAnalyticsRegisterValues(analyticsContext);

  const mainNavigate = workspace.displaySetupWizard
    ? CloudRoutes.Onboarding
    : CloudRoutes.Connections;

  return (
    <Routes>
      <Route path={CloudRoutes.Destination}>
        <DestinationPage />
      </Route>
      <Route path={CloudRoutes.Source}>
        <SourcesPage />
      </Route>
      <Route path={CloudRoutes.Connections}>
        <ConnectionPage />
      </Route>
      <Route path={CloudRoutes.Settings}>
        <Suspense fallback={LoadingPage}>
          <CloudSettingsPage />
        </Suspense>
      </Route>
      <Route path={CloudRoutes.Credits}>
        <CreditsPage />
      </Route>
      {workspace.displaySetupWizard && (
        <Route path={CloudRoutes.Onboarding}>
          <OnboardingServiceProvider>
            <OnboardingPage />
          </OnboardingServiceProvider>
        </Route>
      )}
      <Navigate to={mainNavigate} />
    </Routes>
  );
};

const MainViewRoutes = () => {
  useApiHealthPoll();
  useIntercom();

  const { workspaceId } = useCurrentWorkspace();

  return (
    <Routes>
      <Route path={CloudRoutes.AuthFlow}>
        <CompleteOauthRequest />
      </Route>
      <Route>
        {workspaceId ? (
          <MainView>
            <Suspense fallback={<LoadingPage />}>
              <MainRoutes currentWorkspaceId={workspaceId} />
            </Suspense>
          </MainView>
        ) : (
          <Routes>
            <Route path={CloudRoutes.SelectWorkspace}>
              <WorkspacesPage />
            </Route>
            <Navigate to={CloudRoutes.SelectWorkspace} />
          </Routes>
        )}
      </Route>
    </Routes>
  );
};

export const Routing: React.FC = () => {
  const { user, inited, emailVerified } = useAuthService();
  const config = useConfig();
  useFullStory(config.fullstory, config.fullstory.enabled);

  const analyticsContext = useMemo(
    () =>
      user
        ? {
            cloud_user_id: user.userId,
          }
        : null,
    [user]
  );
  useAnalyticsRegisterValues(analyticsContext);
  useAnalyticsIdentifyUser(user?.userId);

  return (
    <Router>
      <TrackPageAnalytics />
      <Suspense fallback={<LoadingPage />}>
        {inited ? (
          <>
            {user && emailVerified && (
              <WorkspaceServiceProvider>
                <MainViewRoutes />
              </WorkspaceServiceProvider>
            )}
            {user && !emailVerified && (
              <Routes>
                <Route path={CloudRoutes.FirebaseAction}>
                  <VerifyEmailAction />
                </Route>
                <Route path={CloudRoutes.ConfirmVerifyEmail}>
                  <ConfirmEmailPage />
                </Route>
                <Navigate to={CloudRoutes.ConfirmVerifyEmail} />
              </Routes>
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
