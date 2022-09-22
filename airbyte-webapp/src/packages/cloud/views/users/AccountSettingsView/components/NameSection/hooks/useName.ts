import { FormikHelpers } from "formik/dist/types";
import { useState } from "react";
import { useIntl } from "react-intl";

import { useAuthService } from "packages/cloud/services/auth/AuthService";

import { FormValues } from "../types";

type UseNameHook = () => {
  successMessage: string;
  errorMessage: string;
  changeName: (values: FormValues, { setSubmitting, setFieldValue }: FormikHelpers<FormValues>) => Promise<void>;
};

export const useChangeName: UseNameHook = () => {
  const { updateName } = useAuthService();
  const { formatMessage } = useIntl();
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");

  const changeName = async (values: FormValues, { setSubmitting }: FormikHelpers<FormValues>) => {
    setSubmitting(true);

    setSuccessMessage("");
    setErrorMessage("");

    try {
      await updateName(values.name);

      setSuccessMessage(
        formatMessage({
          id: "settings.accountSettings.updateNameSuccess",
        })
      );
    } catch (err) {
      setErrorMessage(
        formatMessage({
          id: "settings.accountSettings.updateNameError",
        }) + JSON.stringify(err)
      );
    }

    setSubmitting(false);
  };

  return { successMessage, errorMessage, changeName };
};
