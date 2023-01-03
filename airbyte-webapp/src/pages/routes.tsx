import React from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

import ApiErrorBoundary from "components/ApiErrorBoundary";

// import { useAnalyticsIdentifyUser, useAnalyticsRegisterValues } from "hooks/services/Analytics";
import { useUser } from "core/AuthContext";
import { useApiHealthPoll } from "hooks/services/Health";
// import { useUserDetailPoll } from "hooks/services/UserDetail";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
// import { useListWorkspaces } from "services/workspaces/WorkspacesService";
import { storeUtmFromQuery } from "utils/utmStorage";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import MainView from "views/layout/MainView";

import { WorkspaceRead } from "../core/request/AirbyteClient";
import { LoginPage } from "./AuthPage/LoginPage";
import SignupPage from "./AuthPage/SignupPage";
import UserSignupPage from "./AuthPage/UserSignupPage";
import ConnectionPage from "./ConnectionPage";
import DestinationPage from "./DestinationPage";
// import OnboardingPage from "./OnboardingPage";
import PaymentErrorPage from "./PaymentErrorPage";
import PaymentPage from "./PaymentPage";
import PreferencesPage from "./PreferencesPage";
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
            <Route path={`${RoutePaths.Payment}/*`} element={<PaymentPage />} />
            <Route path={`${RoutePaths.PaymentError}/*`} element={<PaymentErrorPage />} />
            {/* {workspace ? <Route path={`${RoutePaths.Onboarding}/*`} element={<OnboardingPage />} /> : null}
          <Route path="*" element={<Navigate to={workspace ? RoutePaths.Onboarding : RoutePaths.Connections} />} /> */}
            <Route path="*" element={<Navigate to={RoutePaths.Connections} />} />
          </Routes>
        </ApiErrorBoundary>
      </MainView>
    );
  };

const PreferencesRoutes = () => (
  <Routes>
    <Route path={RoutePaths.Preferences} element={<PreferencesPage />} />
    <Route path="*" element={<Navigate to={RoutePaths.Preferences} />} />
  </Routes>
);

const AuthRoutes = () => (
  <Routes>
    <Route path={`${RoutePaths.Signin}`} element={<LoginPage />} />
    <Route path={`${RoutePaths.Signup}`} element={<SignupPage />} />
    <Route path={`${RoutePaths.UserSignup}`} element={<UserSignupPage />} />
    <Route path="*" element={<AutoMoveToAuth />} />
  </Routes>
);

export const AutoMoveToAuth = () => {
  return <Navigate to={`/${RoutePaths.Signin}`} replace />;
};

// export const AutoSelectFirstWorkspace: React.FC<{ includePath?: boolean }> = ({ includePath }) => {
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
export const AutoSelectFirstWorkspace: React.FC = () => {
  const location = useLocation();

  return <Navigate to={`/${location.pathname}`} replace />;
};

const RoutingWithWorkspace: React.FC = () => {
  const workspace = useCurrentWorkspace();
  // useAddAnalyticsContextForWorkspace(workspace);
  useApiHealthPoll();
  // useUserDetailPoll();

  return (
    <OnboardingServiceProvider>
      {workspace.initialSetupComplete ? <MainViewRoutes workspace={workspace} /> : <PreferencesRoutes />}
    </OnboardingServiceProvider>
  );
};

export const Routing: React.FC = () => {
  const { search } = useLocation();
  const { user } = useUser();

  useEffectOnce(() => {
    storeUtmFromQuery(search);
  });

  // TODO: Remove this after it is verified there are no problems with current routing
  // const OldRoutes = useMemo(
  //   () =>
  //     Object.values(RoutePaths).map((r) => (
  //       <Route path={`${r}/*`} key={r} element={<AutoSelectFirstWorkspace includePath />} />
  //     )),
  //   []
  // );

  return (
    <>
      {user.token && (
        <Routes>
          {/* {OldRoutes} */}
          <Route path={RoutePaths.AuthFlow} element={<CompleteOauthRequest />} />
          {/* TODO: Xuan Ma told me to remove workspaceId from URLs
          <Route path={`${RoutePaths.Workspaces}/:workspaceId/*`} element={<RoutingWithWorkspace />} /> */}
          <Route path="/*" element={<RoutingWithWorkspace />} />
          <Route path="*" element={<AutoSelectFirstWorkspace />} />
        </Routes>
      )}
      {!user.token && <AuthRoutes />}
    </>
  );
};
