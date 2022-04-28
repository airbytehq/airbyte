import { AuthErrorCodes } from "firebase/auth";
import { FormikHelpers } from "formik/dist/types";
import { useState } from "react";
import { useIntl } from "react-intl";

import { useAuthService, useCurrentUser } from "packages/cloud/services/auth/AuthService";

import { FormValues } from "../typings";

type UsePasswordHook = () => {
  successMessage: string;
  errorMessage: string;
  changePassword: (values: FormValues, { setSubmitting, setFieldValue }: FormikHelpers<FormValues>) => void;
};

const usePassword: UsePasswordHook = () => {
  const { updatePassword } = useAuthService();
  const { email } = useCurrentUser();
  const { formatMessage } = useIntl();
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");

  const changePassword = async (values: FormValues, { setSubmitting, setFieldValue }: FormikHelpers<FormValues>) => {
    setSubmitting(true);

    setSuccessMessage("");
    setErrorMessage("");

    if (values.newPassword !== values.passwordConfirmation) {
      setErrorMessage(
        formatMessage({
          id: "settings.accountSettings.error.newPasswordMismatch",
        })
      );

      setSubmitting(false);

      return;
    }

    if (values.currentPassword === values.newPassword) {
      setErrorMessage(
        formatMessage({
          id: "settings.accountSettings.error.newPasswordSameAsCurrent",
        })
      );
      setSubmitting(false);

      return;
    }

    try {
      await updatePassword(email, values.currentPassword, values.newPassword);

      setSuccessMessage(
        formatMessage({
          id: "settings.accountSettings.updatePasswordSuccess",
        })
      );
      setFieldValue("currentPassword", "");
      setFieldValue("newPassword", "");
      setFieldValue("passwordConfirmation", "");
    } catch (err) {
      switch (err.code) {
        case AuthErrorCodes.INVALID_PASSWORD:
          setErrorMessage(
            formatMessage({
              id: "firebase.auth.error.invalidPassword",
            })
          );
          break;
        case AuthErrorCodes.NETWORK_REQUEST_FAILED:
          setErrorMessage(
            formatMessage({
              id: "firebase.auth.error.networkRequestFailed",
            })
          );
          break;
        case AuthErrorCodes.TOO_MANY_ATTEMPTS_TRY_LATER:
          setErrorMessage(
            formatMessage({
              id: "firebase.auth.error.tooManyRequests",
            })
          );
          break;
        default:
          setErrorMessage(
            formatMessage({
              id: "settings.accountSettings.updatePasswordError",
            }) + JSON.stringify(err)
          );
      }
    }

    setSubmitting(false);
  };

  return { successMessage, errorMessage, changePassword };
};

export default usePassword;
