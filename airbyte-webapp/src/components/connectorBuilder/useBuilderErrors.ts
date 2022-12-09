import { flatten } from "flat";
import { FormikErrors, useFormikContext } from "formik";

import { BuilderFormValues } from "./types";

export const useBuilderErrors = () => {
  const { errors, validateForm, setFieldTouched } = useFormikContext<BuilderFormValues>();

  // Returns true if the global config fields or any stream config fields have errors in the provided formik errors, and false otherwise.
  // If limitToStream is provided, the error check is limited to global and the provided stream number.
  const hasErrors = (limitToStream?: number, inputErrors?: FormikErrors<BuilderFormValues>) => {
    const errorsToCheck = inputErrors !== undefined ? inputErrors : errors;

    const invalidViews = Object.keys(errorsToCheck);
    if (invalidViews.length === 0) {
      return false;
    }

    if (invalidViews.includes("global")) {
      return true;
    }

    if (invalidViews.includes("streams")) {
      const invalidStreamNums = Object.keys(errorsToCheck.streams ?? {});
      if (limitToStream !== undefined) {
        return invalidStreamNums.includes(limitToStream.toString());
      }
      return invalidStreamNums.length !== 0;
    }

    return false;
  };

  const validateAndTouch = (callback: () => void, limitToStream?: number) => {
    validateForm().then((errors) => {
      // touch all erroring fields
      for (const path of Object.keys(flatten(errors))) {
        setFieldTouched(path);
      }

      // only call callback if there are no relevant errors
      if (!hasErrors(limitToStream, errors)) {
        callback();
      }
    });
  };

  return { hasErrors, validateAndTouch };
};
