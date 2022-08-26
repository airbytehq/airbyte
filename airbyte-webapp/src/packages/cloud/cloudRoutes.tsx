import React, { Suspense, useEffect, useMemo } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

import ApiErrorBoundary from "components/ApiErrorBoundary";
import LoadingPage from "components/LoadingPage";

import { useAnalyticsIdentifyUser, useAnalyticsRegisterValues } from "hooks/services/Analytics/useAnalyticsService";
import { useTrackPageAnalytics } from "hooks/services/Analytics/useTrackPageAnalytics";
import { FeatureItem, FeatureSet, useFeatureService } from "hooks/services/Feature";
import { useApiHealthPoll } from "hooks/services/Health";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
import useRouter from "hooks/useRouter";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useIntercom } from "packages/cloud/services/thirdParty/intercom/useIntercom";
import { Auth } from "packages/cloud/views/auth";
import { CreditsPage } from "packages/cloud/views/credits";
import MainView from "packages/cloud/views/layout/MainView";
import { WorkspacesPage } from "packages/cloud/views/workspaces";
import ConnectionPage from "pages/ConnectionPage";
import DestinationPage from "pages/DestinationPage";
import OnboardingPage from "pages/OnboardingPage";
import SourcesPage from "pages/SourcesPage";
import { useCurrentWorkspace, WorkspaceServiceProvider } from "services/workspaces/WorkspacesService";
import { storeUtmFromQuery } from "utils/utmStorage";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";

import { RoutePaths } from "../../pages/routePaths";
import { CreditStatus } from "./lib/domain/cloudWorkspaces/types";
import { useConfig } from "./services/config";
import useFullStory from "./services/thirdParty/fullstory/useFullStory";
import { LDExperimentServiceProvider } from "./services/thirdParty/launchdarkly";
import { useGetCloudWorkspace } from "./services/workspaces/WorkspacesService";
import { DefaultView } from "./views/DefaultView";
import { VerifyEmailAction } from "./views/FirebaseActionRoute";
import { CloudSettingsPage } from "./views/settings/CloudSettingsPage";

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

  // Firebase action routes
  // These URLs come from Firebase emails, and all have the same
  // action URL ("/verify-email") with different "mode" parameter
  // TODO: use a better action URL in Firebase email template
  FirebaseAction: "/verify-email",
} as const;

const MainRoutes: React.FC = () => {
  const { setWorkspaceFeatures } = useFeatureService();
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);

  useEffect(() => {
    const outOfCredits =
      cloudWorkspace.creditStatus === CreditStatus.NEGATIVE_BEYOND_GRACE_PERIOD ||
      cloudWorkspace.creditStatus === CreditStatus.NEGATIVE_MAX_THRESHOLD;
    // If the workspace is out of credits it doesn't allow creation of new connections
    // or syncing existing connections.
    setWorkspaceFeatures(
      outOfCredits ? ({ [FeatureItem.AllowCreateConnection]: false, [FeatureItem.AllowSync]: false } as FeatureSet) : []
    );
    return () => {
      setWorkspaceFeatures(undefined);
    };
  }, [cloudWorkspace.creditStatus, setWorkspaceFeatures]);

  const analyticsContext = useMemo(
    () => ({
      workspace_id: workspace.workspaceId,
      customer_id: workspace.customerId,
    }),
    [workspace]
  );
  useAnalyticsRegisterValues(analyticsContext);

  const mainNavigate = workspace.displaySetupWizard ? RoutePaths.Onboarding : RoutePaths.Connections;

  return (
    <ApiErrorBoundary>
      <Routes>
        <Route path={`${RoutePaths.Destination}/*`} element={<DestinationPage />} />
        <Route path={`${RoutePaths.Source}/*`} element={<SourcesPage />} />
        <Route path={`${RoutePaths.Connections}/*`} element={<ConnectionPage />} />
        <Route path={`${RoutePaths.Settings}/*`} element={<CloudSettingsPage />} />
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
    </ApiErrorBoundary>
  );
};

const MainViewRoutes = () => {
  useApiHealthPoll();
  useIntercom();
  const { query } = useRouter();

  return (
    <Routes>
      {[CloudRoutes.Login, CloudRoutes.Signup, CloudRoutes.FirebaseAction].map((r) => (
        <Route key={r} path={`${r}/*`} element={query.from ? <Navigate to={query.from} replace /> : <DefaultView />} />
      ))}
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
  const { user, inited, providers } = useAuthService();
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
  useAnalyticsIdentifyUser(user?.userId, { providers });
  useTrackPageAnalytics();

  if (!inited) {
    return <LoadingPage />;
  }

  return (
    <WorkspaceServiceProvider>
      <LDExperimentServiceProvider>
        <Suspense fallback={<LoadingPage />}>
          {/* Allow email verification no matter whether the user is logged in or not */}
          <Routes>
            <Route path={CloudRoutes.FirebaseAction} element={<VerifyEmailAction />} />
          </Routes>
          {/* Show the login screen if the user is not logged in */}
          {!user && <Auth />}
          {/* Allow all regular routes if the user is logged in */}
          {user && <MainViewRoutes />}
        </Suspense>
      </LDExperimentServiceProvider>
    </WorkspaceServiceProvider>
  );
};
