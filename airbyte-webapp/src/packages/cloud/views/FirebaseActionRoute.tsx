import React from "react";
import { useAsync } from "react-use";

import useRouter from "hooks/useRouter";
import LoadingPage from "components/LoadingPage";

import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { ResetPasswordConfirmPage } from "./auth/ConfirmPasswordResetPage";

export enum FirebaseActionMode {
  VERIFY_EMAIL = "verifyEmail",
  RESET_PASSWORD = "resetPassword",
}

export const VerifyEmailAction: React.FC = () => {
  const { query } = useRouter<{ oobCode: string }>();
  const { verifyEmail } = useAuthService();

  useAsync(async () => await verifyEmail(query.oobCode), []);

  return <LoadingPage />;
};

export const ResetPasswordAction: React.FC = () => {
  const { query } = useRouter<{ mode: string }>();

  if (query.mode === FirebaseActionMode.RESET_PASSWORD) {
    return <ResetPasswordConfirmPage />;
  }
  return <LoadingPage />;
};
