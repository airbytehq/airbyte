import { flatten } from "flat";
import { FormikErrors, useFormikContext } from "formik";
import intersection from "lodash/intersection";
import { useCallback } from "react";

import { BuilderView, useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "./types";

export const useBuilderErrors = () => {
  const { touched, errors, validateForm, setFieldTouched } = useFormikContext<BuilderFormValues>();
  const { setSelectedView } = useConnectorBuilderFormState();

  const invalidViews = useCallback(
    (ignoreUntouched: boolean, limitToViews?: BuilderView[], inputErrors?: FormikErrors<BuilderFormValues>) => {
      const errorsToCheck = inputErrors !== undefined ? inputErrors : errors;
      const errorKeys = Object.keys(errorsToCheck);

      const invalidViews: BuilderView[] = [];

      if (errorKeys.includes("global")) {
        if (ignoreUntouched) {
          if (errorsToCheck.global && touched.global) {
            const globalErrorKeys = Object.keys(flatten(errorsToCheck.global));
            const globalTouchedKeys = Object.keys(flatten(touched.global));
            if (intersection(globalErrorKeys, globalTouchedKeys).length > 0) {
              invalidViews.push("global");
            }
          }
        } else {
          invalidViews.push("global");
        }
      }

      if (errorKeys.includes("streams")) {
        const errorStreamNums = Object.keys(errorsToCheck.streams ?? {});

        if (ignoreUntouched) {
          if (errorsToCheck.streams && touched.streams) {
            // loop over each stream and find ones with fields that are both touched and erroring
            for (const streamNumString of errorStreamNums) {
              const streamNum = Number(streamNumString);
              const streamErrors = errorsToCheck.streams[streamNum];
              const streamTouched = touched.streams[streamNum];
              if (streamErrors && streamTouched) {
                const streamErrorKeys = Object.keys(flatten(streamErrors));
                const streamTouchedKeys = Object.keys(flatten(streamTouched));
                if (intersection(streamErrorKeys, streamTouchedKeys).length > 0) {
                  invalidViews.push(streamNum);
                }
              }
            }
          }
        } else {
          invalidViews.push(...errorStreamNums.map((numString) => Number(numString)));
        }
      }

      return limitToViews === undefined ? invalidViews : intersection(invalidViews, limitToViews);
    },
    [errors, touched]
  );

  // Returns true if the global config fields or any stream config fields have errors in the provided formik errors, and false otherwise.
  // If limitToViews is provided, the error check is limited to only those views.
  const hasErrors = useCallback(
    (ignoreUntouched: boolean, limitToViews?: BuilderView[]) => {
      return invalidViews(ignoreUntouched, limitToViews).length > 0;
    },
    [invalidViews]
  );

  const validateAndTouch = useCallback(
    (callback: () => void, limitToViews?: BuilderView[]) => {
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
          }
        } else {
          callback();
        }
      });
    },
    [invalidViews, setFieldTouched, setSelectedView, validateForm]
  );

  return { hasErrors, validateAndTouch };
};
