import React from "react";
import { useIntl } from "react-intl";
import { Navigate, useNavigate } from "react-router-dom";
import { useAsync } from "react-use";

import LoadingPage from "components/LoadingPage";

import { useNotificationService } from "hooks/services/Notification";
import useRouter from "hooks/useRouter";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import { CloudRoutes } from "../cloudRoutes";
import { AcceptEmailInvite } from "./AcceptEmailInvite";
import { ResetPasswordConfirmPage } from "./auth/ConfirmPasswordResetPage";

export enum FirebaseActionMode {
  VERIFY_EMAIL = "verifyEmail",
  RESET_PASSWORD = "resetPassword",
  SIGN_IN = "signIn",
}

export const VerifyEmailAction: React.FC = () => {
  const { query } = useRouter<{ oobCode: string; mode: string }>();
  const { verifyEmail } = useAuthService();
  const navigate = useNavigate();
  const { formatMessage } = useIntl();
  const { registerNotification } = useNotificationService();

  useAsync(async () => {
    if (query.mode === FirebaseActionMode.VERIFY_EMAIL) {
      // Send verification code to authentication service
      await verifyEmail(query.oobCode);
      // Show a notification that the mail got verified successfully
      registerNotification({
        id: "auth/email-verified",
        title: formatMessage({ id: "verifyEmail.notification" }),
        isError: false,
      });
      // Navigate the user to the homepage
      navigate("/");
    }
  }, []);

  // Only render the loading screen if we're verifying an email otherwise don't render anything,
  // since password reset is handled in a different place.
  return query.mode === FirebaseActionMode.VERIFY_EMAIL ? <LoadingPage /> : null;
};

export const FirebaseActionRoute: React.FC = () => {
  const { query: { mode } = {} } = useRouter<{ mode: string }>();

  switch (mode) {
    case FirebaseActionMode.VERIFY_EMAIL:
      return <VerifyEmailAction />;

    case FirebaseActionMode.RESET_PASSWORD:
      return <ResetPasswordConfirmPage />;

    case FirebaseActionMode.SIGN_IN:
      return <AcceptEmailInvite />;

    default:
      return <Navigate to={CloudRoutes.Login} replace />;
  }
};
