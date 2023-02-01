import React, { Suspense, useEffect, useMemo } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

import { ApiErrorBoundary } from "components/common/ApiErrorBoundary";
import LoadingPage from "components/LoadingPage";

import { useAnalyticsIdentifyUser, useAnalyticsRegisterValues } from "hooks/services/Analytics/useAnalyticsService";
import { FeatureItem, FeatureSet, useFeatureService } from "hooks/services/Feature";
import { useApiHealthPoll } from "hooks/services/Health";
import { useQuery } from "hooks/useQuery";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useCurrentWorkspace, WorkspaceServiceProvider } from "services/workspaces/WorkspacesService";
import { setSegmentAnonymousId, useGetSegmentAnonymousId } from "utils/crossDomainUtils";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";

import { CloudRoutes } from "./cloudRoutePaths";
import { CreditStatus } from "./lib/domain/cloudWorkspaces/types";
import { LDExperimentServiceProvider } from "./services/thirdParty/launchdarkly";
import { useGetCloudWorkspace } from "./services/workspaces/CloudWorkspacesService";
import { VerifyEmailAction } from "./views/FirebaseActionRoute";
import { RoutePaths, DestinationPaths } from "../../pages/routePaths";

const MainView = React.lazy(() => import("packages/cloud/views/layout/MainView"));
const WorkspacesPage = React.lazy(() => import("packages/cloud/views/workspaces"));
const Auth = React.lazy(() => import("packages/cloud/views/auth"));
const CreditsPage = React.lazy(() => import("packages/cloud/views/credits"));

const ConnectionsRoutes = React.lazy(() => import("pages/connections/ConnectionsRoutes"));
const CreateConnectionPage = React.lazy(() => import("pages/connections/CreateConnectionPage"));
const AllDestinationsPage = React.lazy(() => import("pages/destination/AllDestinationsPage"));
const CreateDestinationPage = React.lazy(() => import("pages/destination/CreateDestinationPage"));
const DestinationItemPage = React.lazy(() => import("pages/destination/DestinationItemPage"));
const DestinationOverviewPage = React.lazy(() => import("pages/destination/DestinationOverviewPage"));
const DestinationSettingsPage = React.lazy(() => import("pages/destination/DestinationSettingsPage"));
const SourcesPage = React.lazy(() => import("pages/SourcesPage"));
const SpeakeasyRedirectPage = React.lazy(() => import("pages/SpeakeasyRedirectPage"));

const CloudSettingsPage = React.lazy(() => import("./views/settings/CloudSettingsPage"));
const DefaultView = React.lazy(() => import("./views/DefaultView"));

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
    setWorkspaceFeatures(outOfCredits ? ({ [FeatureItem.AllowSync]: false } as FeatureSet) : []);
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

  return (
    <ApiErrorBoundary>
      <Routes>
        <Route path={RoutePaths.Destination}>
          <Route index element={<AllDestinationsPage />} />
          <Route path={DestinationPaths.NewDestination} element={<CreateDestinationPage />} />
          <Route path={DestinationPaths.NewConnection} element={<CreateConnectionPage />} />
          <Route path={DestinationPaths.Root} element={<DestinationItemPage />}>
            <Route path={DestinationPaths.Settings} element={<DestinationSettingsPage />} />
            <Route index element={<DestinationOverviewPage />} />
          </Route>
        </Route>
        <Route path={`${RoutePaths.Source}/*`} element={<SourcesPage />} />
        <Route path={`${RoutePaths.Connections}/*`} element={<ConnectionsRoutes />} />
        <Route path={`${RoutePaths.Settings}/*`} element={<CloudSettingsPage />} />
        <Route path={CloudRoutes.Credits} element={<CreditsPage />} />
        <Route path="*" element={<Navigate to={RoutePaths.Connections} replace />} />
      </Routes>
    </ApiErrorBoundary>
  );
};

const MainViewRoutes = () => {
  useApiHealthPoll();
  const query = useQuery<{ from: string }>();

  return (
    <Routes>
      <Route path={RoutePaths.SpeakeasyRedirect} element={<SpeakeasyRedirectPage />} />
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
  const { user, inited, providers, hasCorporateEmail } = useAuthService();

  const { search } = useLocation();

  useEffectOnce(() => {
    setSegmentAnonymousId(search);
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

  const userTraits = useMemo(
    () => (user ? { providers, email: user.email, isCorporate: hasCorporateEmail() } : {}),
    [hasCorporateEmail, providers, user]
  );

  useGetSegmentAnonymousId();
  useAnalyticsRegisterValues(analyticsContext);
  useAnalyticsIdentifyUser(user?.userId, userTraits);

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
