import { flatten } from "flat";
import { FormikErrors, useFormikContext } from "formik";
import intersection from "lodash/intersection";

import { BuilderView } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "./types";

export const useBuilderErrors = () => {
  const { touched, errors, validateForm, setFieldTouched } = useFormikContext<BuilderFormValues>();

  // Returns true if the global config fields or any stream config fields have errors in the provided formik errors, and false otherwise.
  // If limitToViews is provided, the error check is limited to only those views.
  const hasErrors = (
    ignoreUntouched: boolean,
    limitToViews?: BuilderView[],
    inputErrors?: FormikErrors<BuilderFormValues>
  ) => {
    const errorsToCheck = inputErrors !== undefined ? inputErrors : errors;

    const errorViews = Object.keys(errorsToCheck);
    const invalidViews = ignoreUntouched ? intersection(errorViews, Object.keys(touched)) : errorViews;
    if (invalidViews.length === 0) {
      return false;
    }

    if (invalidViews.includes("global")) {
      if (limitToViews === undefined || limitToViews.includes("global")) {
        return true;
      }
    }

    if (invalidViews.includes("streams")) {
      const errorStreamNums = Object.keys(errorsToCheck.streams ?? {});
      const invalidStreamNums = (
        ignoreUntouched ? intersection(errorStreamNums, Object.keys(touched.streams ?? {})) : errorStreamNums
      ).map((numString) => Number(numString));

      return limitToViews === undefined || intersection(limitToViews, invalidStreamNums).length > 0;
    }

    return false;
  };

  const validateAndTouch = (callback: () => void, limitToViews?: BuilderView[]) => {
    validateForm().then((errors) => {
      for (const path of Object.keys(flatten(errors))) {
        setFieldTouched(path);
      }

      // only call callback if there are no relevant errors
      if (!hasErrors(false, limitToViews, errors)) {
        callback();
      }
    });
  };

  return { hasErrors, validateAndTouch };
};
