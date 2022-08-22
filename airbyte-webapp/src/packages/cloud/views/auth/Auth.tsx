import React, { Suspense } from "react";
import { useIntl } from "react-intl";
import { Navigate, Route, Routes } from "react-router-dom";

import { LoadingPage } from "components";

import { useExperiment } from "hooks/services/Experiment";
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

const hasValidRightSideUrl = (url?: string): boolean => {
  if (url) {
    try {
      const parsedUrl = new URL(url);
      const isValid = parsedUrl.protocol === "https:" && parsedUrl.hostname.endsWith("airbyte.com");
      if (!isValid) {
        console.warn(`${parsedUrl} is not valid.`);
      }
      return isValid;
    } catch (e) {
      console.warn(e);
    }
  }

  return false;
};

const Auth: React.FC = () => {
  const { pathname, location } = useRouter();
  const { formatMessage } = useIntl();
  const { loggedOut } = useAuthService();
  const rightSideUrl = useExperiment("authPage.rightSideUrl", undefined);

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
        {hasValidRightSideUrl(rightSideUrl) ? (
          <iframe
            className={styles.rightSideFrame}
            src={rightSideUrl}
            scrolling="no"
            title={formatMessage({ id: "login.rightSideFrameTitle" })}
          />
        ) : (
          <PersonQuoteCover />
        )}
      </div>
    </div>
  );
};

export default Auth;
