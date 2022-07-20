import { FormikErrors } from "formik";
import { useIntl } from "react-intl";

import { FormValues } from "./types";

export const useValidation = () => {
  const { formatMessage } = useIntl();
  return (values: FormValues): FormikErrors<FormValues> => {
    const errors: FormikErrors<FormValues> = {};
    if (values.name.length === 0) {
      errors.name = formatMessage({ id: "settings.accountSettings.name.empty.error" });
    }
    return errors;
  };
};
