import React, { useMemo } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

import ApiErrorBoundary from "components/ApiErrorBoundary";

// import { useAnalyticsIdentifyUser, useAnalyticsRegisterValues } from "hooks/services/Analytics";
import { useApiHealthPoll } from "hooks/services/Health";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
// import { useCurrentWorkspace } from "hooks/services/useWorkspace";
// import { useListWorkspaces } from "services/workspaces/WorkspacesService";
import { storeUtmFromQuery } from "utils/utmStorage";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import MainView from "views/layout/MainView";

import { WorkspaceRead } from "../core/request/AirbyteClient";
import {
  // AuthenticatedUser,
  getAuthenticatedUser,
} from "../services/auth/AuthService";
import { LoginPage } from "./AuthPage/LoginPage";
import SignupPage from "./AuthPage/SignupPage";
import ConnectionPage from "./ConnectionPage";
import DestinationPage from "./DestinationPage";
// import OnboardingPage from "./OnboardingPage";
// import PreferencesPage from "./PreferencesPage";
import { RoutePaths } from "./routePaths";
import SettingsPage from "./SettingsPage";
import SourcesPage from "./SourcesPage";

// const useAddAnalyticsContextForWorkspace = (workspace: WorkspaceRead): void => {
//   const analyticsContext = useMemo(
//     () => ({
//       workspace_id: workspace.workspaceId,
//       customer_id: workspace.customerId,
//     }),
//     [workspace.workspaceId, workspace.customerId]
//   );
//   useAnalyticsRegisterValues(analyticsContext);
//   useAnalyticsIdentifyUser(workspace.workspaceId);
// };

const MainViewRoutes: React.FC<{ workspace: WorkspaceRead }> = () =>
  // { workspace }
  {
    return (
      <MainView>
        <ApiErrorBoundary>
          <Routes>
            <Route path={`${RoutePaths.Destination}/*`} element={<DestinationPage />} />
            <Route path={`${RoutePaths.Source}/*`} element={<SourcesPage />} />
            <Route path={`${RoutePaths.Connections}/*`} element={<ConnectionPage />} />
            <Route path={`${RoutePaths.Settings}/*`} element={<SettingsPage />} />
            {/* {workspace ? <Route path={`${RoutePaths.Onboarding}/*`} element={<OnboardingPage />} /> : null}
          <Route path="*" element={<Navigate to={workspace ? RoutePaths.Onboarding : RoutePaths.Connections} />} /> */}
            <Route path="*" element={<Navigate to={RoutePaths.Connections} />} />
          </Routes>
        </ApiErrorBoundary>
      </MainView>
    );
  };

// const PreferencesRoutes = () => (
//   <Routes>
//     <Route path={RoutePaths.Preferences} element={<PreferencesPage/>} />
//     <Route path="*" element={<Navigate to={RoutePaths.Preferences} />} />
//   </Routes>
// );

const AuthRoutes = () => (
  <Routes>
    <Route path={`${RoutePaths.Signin}`} element={<LoginPage />} />
    <Route path={`${RoutePaths.Signup}`} element={<SignupPage />} />
    <Route path="*" element={<AutoMoveToAuth />} />
  </Routes>
);

export const AutoMoveToAuth = () => {
  return <Navigate to={`/${RoutePaths.Signin}`} replace />;
};

export const AutoSelectFirstWorkspace: React.FC<{ includePath?: boolean }> = ({ includePath }) => {
  // const location = useLocation();
  // const workspaces = useListWorkspaces();
  // const currentWorkspace = workspaces[0];
  //
  // return (
  //   <Navigate
  //     to={`/${RoutePaths.Workspaces}/${currentWorkspace.workspaceId}${includePath ? location.pathname : ""}`}
  //     replace
  //   />
  // );
  const location = useLocation();
  const user = getAuthenticatedUser();

  return (
    <Navigate to={`/${RoutePaths.Workspaces}/${user.workspaceId}${includePath ? location.pathname : ""}`} replace />
  );
};

const RoutingWithWorkspace: React.FC = () => {
  // const workspace = useCurrentWorkspace();
  // useAddAnalyticsContextForWorkspace(workspace);
  useApiHealthPoll();
  const user = getAuthenticatedUser();

  return (
    <OnboardingServiceProvider>
      {/* {workspace.initialSetupComplete ? <MainViewRoutes workspace={workspace} /> : <PreferencesRoutes />}*/}
      <MainViewRoutes workspace={user.workspaceId} />
    </OnboardingServiceProvider>
  );
};

export const Routing: React.FC = () => {
  const { search } = useLocation();

  useEffectOnce(() => {
    storeUtmFromQuery(search);
  });

  // TODO: Remove this after it is verified there are no problems with current routing
  const OldRoutes = useMemo(
    () =>
      Object.values(RoutePaths).map((r) => (
        <Route path={`${r}/*`} key={r} element={<AutoSelectFirstWorkspace includePath />} />
      )),
    []
  );
  const user = getAuthenticatedUser();
  return (
    <>
      {user && (
        <Routes>
          {OldRoutes}
          <Route path={RoutePaths.AuthFlow} element={<CompleteOauthRequest />} />

          <Route path={`${RoutePaths.Workspaces}/:workspaceId/*`} element={<RoutingWithWorkspace />} />
          <Route path="*" element={<AutoSelectFirstWorkspace />} />
        </Routes>
      )}
      {!user && <AuthRoutes />}
    </>
  );
};
