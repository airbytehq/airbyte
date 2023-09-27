import React from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffectOnce } from "react-use";

import ApiErrorBoundary from "components/ApiErrorBoundary";

import { useUser } from "core/AuthContext";
import { useAppNotification, appNotificationInitialState } from "hooks/services/AppNotification";
import { useApiHealthPoll } from "hooks/services/Health";
import { OnboardingServiceProvider } from "hooks/services/Onboarding";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { MessageBox } from "pages/SettingsPage/components/MessageBox";
import { storeUtmFromQuery } from "utils/utmStorage";
import { CompleteOauthRequest } from "views/CompleteOauthRequest";
import MainView from "views/layout/MainView";

import LoginNewPage from "./AuthPage/LoginNewPage/LoginNewPage";
// import { LoginPage } from "./AuthPage/LoginPage";
// import ResetPasswordPage from "./AuthPage/ResetPasswordPage";
// import SignupPage from "./AuthPage/SignupPage";
// import UserSignupPage from "./AuthPage/UserSignupPage";
// import VerifyEmailPage from "./AuthPage/VerifyEmailPage";
import ConnectionPage from "./ConnectionPage";
import DestinationPage from "./DestinationPage";
import PaymentErrorPage from "./PaymentErrorPage";
import PaymentPage from "./PaymentPage";
import FailedPaymentPage from "./PaymentPage/FailedPaymentPage";
import PreferencesPage from "./PreferencesPage";
import { RoutePaths } from "./routePaths";
import { SettingsPage } from "./SettingsPage";
import SourcesPage from "./SourcesPage";
import { WorkspaceRead } from "../core/request/AirbyteClient";

const MainViewRoutes: React.FC<{ workspace: WorkspaceRead }> = () => {
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
          <Route path={`${RoutePaths.FailedPayment}/*`} element={<FailedPaymentPage />} />
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
    <Route path={`${RoutePaths.LoginNew}/*`} element={<LoginNewPage />} />
    {/* <Route path={`${RoutePaths.Signin}`} element={<LoginPage />} />
    <Route path={`${RoutePaths.Signup}`} element={<SignupPage />} />
    <Route path={`${RoutePaths.UserSignup}`} element={<UserSignupPage />} />
    <Route path={`${RoutePaths.VerifyEmail}`} element={<VerifyEmailPage />} />
    <Route path={`${RoutePaths.ResetPassword}`} element={<ResetPasswordPage />} /> */}
    <Route path="*" element={<AutoMoveToAuth />} />
  </Routes>
);

export const AutoMoveToAuth = () => {
  return <Navigate to={`/${RoutePaths.LoginNew}${window.location.search}`} replace />;
};
export const AutoSelectFirstWorkspace: React.FC = () => {
  const location = useLocation();

  return <Navigate to={`/${location.pathname}`} replace />;
};

const RoutingWithWorkspace: React.FC = () => {
  const workspace = useCurrentWorkspace();
  useApiHealthPoll();
  const { notification, setNotification } = useAppNotification();

  return (
    <OnboardingServiceProvider>
      <MessageBox
        message={notification.message}
        type={notification.type}
        onClose={() => setNotification(appNotificationInitialState)}
      />
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

  return (
    <>
      {user.token && (
        <Routes>
          <Route path={RoutePaths.AuthFlow} element={<CompleteOauthRequest />} />
          {/* {!user.workspaceId && <Route path={`${RoutePaths.Payment}/*`} element={<PaymentPage />} />}
          {!user.workspaceId && <Route path={`${RoutePaths.Settings}/*`} element={<SettingsPage />} />} */}
          {user.workspaceId && <Route path="/*" element={<RoutingWithWorkspace />} />}
          {user.workspaceId && <Route path="*" element={<AutoSelectFirstWorkspace />} />}
        </Routes>
      )}
      {!user.token && <AuthRoutes />}
    </>
  );
};
