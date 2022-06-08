import { AuthErrorCodes } from "firebase/auth";
import { FormikHelpers } from "formik/dist/types";
import { useState } from "react";
import { useIntl } from "react-intl";

import { useAuthService } from "packages/cloud/services/auth/AuthService";

import { FormValues } from "../typings";

type UseEmailHook = () => {
  successMessage: string;
  errorMessage: string;
  updateEmail: (values: FormValues, { setSubmitting, setFieldValue }: FormikHelpers<FormValues>) => void;
};

const useEmail: UseEmailHook = () => {
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const { formatMessage } = useIntl();
  const { updateEmail } = useAuthService();

  const onUpdateEmail = async (values: FormValues, { setSubmitting, setFieldValue }: FormikHelpers<FormValues>) => {
    setSubmitting(true);

    setSuccessMessage("");
    setErrorMessage("");

    try {
      await updateEmail(values.email, values.password);

      setSuccessMessage(
        formatMessage({
          id: "settings.accountSettings.updateEmailSuccess",
        })
      );
      setFieldValue("password", "");
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
          setErrorMessage(JSON.stringify(err));
      }
    }

    setSubmitting(false);
  };

  return { successMessage, errorMessage, updateEmail: onUpdateEmail };
};

export default useEmail;
