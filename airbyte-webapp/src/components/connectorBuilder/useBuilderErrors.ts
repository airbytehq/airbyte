import { flatten } from "flat";
import { FormikErrors, useFormikContext } from "formik";
import intersection from "lodash/intersection";

import { BuilderView, useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "./types";

export const useBuilderErrors = () => {
  const { touched, errors, validateForm, setFieldTouched } = useFormikContext<BuilderFormValues>();
  const { setSelectedView, setTestStreamIndex } = useConnectorBuilderState();

  const invalidViews = (
    ignoreUntouched: boolean,
    limitToViews?: BuilderView[],
    inputErrors?: FormikErrors<BuilderFormValues>
  ) => {
    const errorsToCheck = inputErrors !== undefined ? inputErrors : errors;

    const errorKeys = ignoreUntouched
      ? intersection(Object.keys(errorsToCheck), Object.keys(touched))
      : Object.keys(errorsToCheck);

    const invalidViews: BuilderView[] = [];

    if (errorKeys.includes("global")) {
      invalidViews.push("global");
    }

    if (errorKeys.includes("streams")) {
      const errorStreamNums = Object.keys(errorsToCheck.streams ?? {});
      const invalidStreamNums = (
        ignoreUntouched ? intersection(errorStreamNums, Object.keys(touched.streams ?? {})) : errorStreamNums
      ).map((numString) => Number(numString));

      invalidViews.push(...invalidStreamNums);
    }

    return limitToViews === undefined ? invalidViews : intersection(invalidViews, limitToViews);
  };

  // Returns true if the global config fields or any stream config fields have errors in the provided formik errors, and false otherwise.
  // If limitToViews is provided, the error check is limited to only those views.
  const hasErrors = (
    ignoreUntouched: boolean,
    limitToViews?: BuilderView[],
    inputErrors?: FormikErrors<BuilderFormValues>
  ) => {
    return invalidViews(ignoreUntouched, limitToViews, inputErrors).length > 0;
  };

  const validateAndTouch = (callback: () => void, limitToViews?: BuilderView[]) => {
    validateForm().then((errors) => {
      for (const path of Object.keys(flatten(errors))) {
        setFieldTouched(path);
      }

      // If there are relevant errors, select the erroring view, prioritizing global
      // Otherwise, execute the callback.

      const invalidBuilderViews = invalidViews(false, limitToViews, errors);

      if (invalidBuilderViews.length > 0) {
        if (invalidBuilderViews.includes("global")) {
          setSelectedView("global");
        } else {
          setSelectedView(invalidBuilderViews[0]);
          setTestStreamIndex(invalidBuilderViews[0] as number);
        }
      } else {
        callback();
      }
    });
  };

  return { hasErrors, validateAndTouch };
};
