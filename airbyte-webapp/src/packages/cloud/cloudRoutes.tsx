import React, { Suspense, useMemo } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

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
import {
  useCurrentWorkspace,
  WorkspaceServiceProvider,
} from "services/workspaces/WorkspacesService";
import OnboardingPage from "pages/OnboardingPage";
import { CreditsPage } from "packages/cloud/views/credits";
import { ConfirmEmailPage } from "./views/auth/ConfirmEmailPage";
import { TrackPageAnalytics } from "hooks/services/Analytics/TrackPageAnalytics";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
import { useConfig } from "./services/config";
import useFullStory from "./services/thirdParty/fullstory/useFullStory";
import {
  useAnalyticsIdentifyUser,
  useAnalyticsRegisterValues,
} from "hooks/services/Analytics/useAnalyticsService";
import { CloudSettingsPage } from "./views/settings/CloudSettingsPage";
import { VerifyEmailAction } from "./views/FirebaseActionRoute";
import useRouter from "hooks/useRouter";
import { storeUtmFromQuery } from "utils/utmStorage";
import { DefaultView } from "./views/DefaultView";
import { hasFromState } from "utils/stateUtils";
import { RoutePaths } from "../../pages/routePaths";
import { FeatureItem, useFeatureRegisterValues } from "hooks/services/Feature";
import { useGetCloudWorkspace } from "./services/workspaces/WorkspacesService";
import { CreditStatus } from "./lib/domain/cloudWorkspaces/types";

export const CloudRoutes = {
  Root: "/",
  AuthFlow: "/auth_flow",

  Metrics: "metrics",
  SelectWorkspace: "workspaces",
  Credits: "credits",

  // Auth routes
  Signup: "/signup",
  Login: "/login",
  ResetPassword: "/reset-password",
  ConfirmVerifyEmail: "/confirm-verify-email",

  // Firebase action routes
  // These URLs come from Firebase emails, and all have the same
  // action URL ("/verify-email") with different "mode" parameter
  // TODO: use a better action URL in Firebase email template
  FirebaseAction: "/verify-email",
} as const;

const MainRoutes: React.FC = () => {
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);

  const analyticsContext = useMemo(
    () => ({
      workspace_id: workspace.workspaceId,
      customer_id: workspace.customerId,
    }),
    [workspace]
  );
  useAnalyticsRegisterValues(analyticsContext);

  const mainNavigate = workspace.displaySetupWizard
    ? RoutePaths.Onboarding
    : RoutePaths.Connections;

  const features = useMemo(
    () =>
      cloudWorkspace.creditStatus !==
        CreditStatus.NEGATIVE_BEYOND_GRACE_PERIOD &&
      cloudWorkspace.creditStatus !== CreditStatus.NEGATIVE_MAX_THRESHOLD
        ? [
            { id: FeatureItem.AllowCreateConnection },
            { id: FeatureItem.AllowSync },
          ]
        : null,
    [cloudWorkspace]
  );

  useFeatureRegisterValues(features);

  return (
    <Routes>
      <Route
        path={`${RoutePaths.Destination}/*`}
        element={<DestinationPage />}
      />
      <Route path={`${RoutePaths.Source}/*`} element={<SourcesPage />} />
      <Route
        path={`${RoutePaths.Connections}/*`}
        element={<ConnectionPage />}
      />
      <Route
        path={`${RoutePaths.Settings}/*`}
        element={<CloudSettingsPage />}
      />
      <Route path={CloudRoutes.Credits} element={<CreditsPage />} />

      {workspace.displaySetupWizard && (
        <Route
          path={RoutePaths.Onboarding}
          element={
            <OnboardingServiceProvider>
              <OnboardingPage />
            </OnboardingServiceProvider>
          }
        />
      )}
      <Route path="*" element={<Navigate to={mainNavigate} replace />} />
    </Routes>
  );
};

const MainViewRoutes = () => {
  useApiHealthPoll();
  useIntercom();
  const { location } = useRouter();

  return (
    <Routes>
      {[CloudRoutes.Login, CloudRoutes.Signup, CloudRoutes.FirebaseAction].map(
        (r) => (
          <Route
            key={r}
            path={`${r}/*`}
            element={
              hasFromState(location.state) ? (
                <Navigate to={location.state.from} replace />
              ) : (
                <DefaultView />
              )
            }
          />
        )
      )}
      <Route path={CloudRoutes.SelectWorkspace} element={<WorkspacesPage />} />
      <Route path={CloudRoutes.AuthFlow} element={<CompleteOauthRequest />} />
      <Route
        path={`${RoutePaths.Workspaces}/:workspaceId/*`}
        element={
          <MainView>
            <MainRoutes />
          </MainView>
        }
      />
      <Route path="*" element={<DefaultView />} />
    </Routes>
  );
};

export const Routing: React.FC = () => {
  const { user, inited, emailVerified } = useAuthService();
  const config = useConfig();
  useFullStory(config.fullstory, config.fullstory.enabled, user);

  const { search } = useLocation();

  useEffectOnce(() => {
    storeUtmFromQuery(search);
  });

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

  if (!inited) {
    return <LoadingPage />;
  }

  return (
    <WorkspaceServiceProvider>
      <TrackPageAnalytics />
      <Suspense fallback={<LoadingPage />}>
        {!user && <Auth />}
        {user && emailVerified && <MainViewRoutes />}
        {user && !emailVerified && (
          <Routes>
            <Route
              path={CloudRoutes.FirebaseAction}
              element={<VerifyEmailAction />}
            />
            <Route
              path={CloudRoutes.ConfirmVerifyEmail}
              element={<ConfirmEmailPage />}
            />
            <Route
              path="*"
              element={<Navigate to={CloudRoutes.ConfirmVerifyEmail} replace />}
            />
          </Routes>
        )}
      </Suspense>
    </WorkspaceServiceProvider>
  );
};
