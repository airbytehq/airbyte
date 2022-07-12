import React, { Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

import useRouter from "hooks/useRouter";
import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { FirebaseActionRoute } from "packages/cloud/views/FirebaseActionRoute";

import styles from "./Auth.module.scss";
import FormContent from "./components/FormContent";
import { PersonQuoteCover } from "./components/PersonQuoteCover";
import { LoginPage } from "./LoginPage";
import { ResetPasswordPage } from "./ResetPasswordPage";
import { SignupPage } from "./SignupPage";

const Auth: React.FC = () => {
  const { pathname, location } = useRouter();
  const { loggedOut } = useAuthService();
  const toLogin = pathname === CloudRoutes.Signup || pathname === CloudRoutes.FirebaseAction;

  return (
    <div className={styles.container}>
      <div className={styles.leftSide}>
        <FormContent toLogin={toLogin}>
          <Suspense fallback={<LoadingPage />}>
            <Routes>
              <Route path={CloudRoutes.Login} element={<LoginPage />} />
              <Route path={CloudRoutes.Signup} element={<SignupPage />} />
              <Route path={CloudRoutes.ResetPassword} element={<ResetPasswordPage />} />
              <Route path={CloudRoutes.FirebaseAction} element={<FirebaseActionRoute />} />
              <Route
                path="*"
                element={<Navigate to={`${CloudRoutes.Login}${loggedOut ? "" : `?from=${location.pathname}`}`} />}
              />
            </Routes>
          </Suspense>
        </FormContent>
      </div>
      <div className={styles.rightSide}>
        <PersonQuoteCover />
      </div>
    </div>
  );
};

export default Auth;
