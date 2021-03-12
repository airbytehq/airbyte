import * as yup from "yup";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import flatten from "flat";
import merge from "lodash.merge";

import { FormBlock, WidgetConfig, WidgetConfigMap } from "core/form/types";
import { jsonSchemaToUiWidget } from "core/jsonSchema/schemaToUiWidget";
import { buildYupFormForJsonSchema } from "core/jsonSchema/schemaToYup";
import { buildPathInitialState } from "core/form/uiWidget";
import { ServiceFormValues } from "./types";

function useBuildForm(
  isLoadingConnectionConfiguration?: boolean,
  initialValues?: Partial<ServiceFormValues>,
  jsonSchema?: JSONSchema7
): {
  initialValues: ServiceFormValues;
  formFields: FormBlock[];
} {
  const startValues = useMemo<ServiceFormValues>(() => {
    const values: ServiceFormValues = {
      name: "",
      serviceType: "",
      ...initialValues,
    };

    return values;
  }, [initialValues]);

  const formFields = useMemo<FormBlock[]>(() => {
    return [
      {
        _type: "formItem",
        type: "string",
        fieldKey: "name",
        fieldName: "name",
        isRequired: true,
      },
      {
        _type: "formItem",
        type: "string",
        fieldKey: "serviceType",
        fieldName: "serviceType",
        isRequired: true,
      },
      ...(jsonSchema && !isLoadingConnectionConfiguration
        ? [jsonSchemaToUiWidget(jsonSchema, "connectionConfiguration")]
        : []),
    ];
  }, [jsonSchema, isLoadingConnectionConfiguration]);

  return {
    initialValues: startValues,
    formFields,
  };
}

const useBuildUiWidgets = (
  formFields: FormBlock[],
  formValues: ServiceFormValues
): {
  uiWidgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (widgetId: string, updatedValues: WidgetConfig) => void;
} => {
  const [overriddenWidgetState, setUiWidgetsInfo] = useState<WidgetConfigMap>(
    {}
  );

  // As schema is dynamic, it is possible, that new updated values, will differ from one stored.
  const mergedState = useMemo(
    () =>
      merge(
        buildPathInitialState(formFields, formValues),
        overriddenWidgetState
      ),
    [formFields, formValues, overriddenWidgetState]
  );

  const setUiWidgetsInfoSubState = useCallback(
    (widgetId: string, updatedValues: WidgetConfig) =>
      setUiWidgetsInfo({ ...mergedState, [widgetId]: updatedValues }),
    [mergedState, setUiWidgetsInfo]
  );

  return {
    uiWidgetsInfo: mergedState,
    setUiWidgetsInfo: setUiWidgetsInfoSubState,
  };
};

// As validation schema depends on what path of oneOf is currently selected in jsonschema
const useConstructValidationSchema = (
  uiWidgetsInfo: WidgetConfigMap,
  jsonSchema?: JSONSchema7
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
): yup.ObjectSchema<any> => {
  return useMemo(() => {
    let validationShape: yup.ObjectSchema = yup.object().shape({
      name: yup.string().required("form.empty.error"),
      serviceType: yup.string().required("form.empty.error"),
    });

    // We have additional fields. Lets build schema for them
    if (jsonSchema?.properties) {
      validationShape = validationShape.shape({
        connectionConfiguration: buildYupFormForJsonSchema(
          jsonSchema,
          uiWidgetsInfo,
          undefined,
          "connectionConfiguration"
        ),
      });
    }

    return validationShape;
  }, [uiWidgetsInfo, jsonSchema]);
};

const usePatchFormik = (): void => {
  const {
    setFieldTouched,
    isSubmitting,
    isValidating,
    validationSchema,
    validateForm,
    errors,
  } = useFormikContext();
  // Formik doesn't validate values again, when validationSchema was changed on the fly.
  useEffect(() => {
    validateForm();
  }, [validateForm, validationSchema]);

  /* Fixes issue https://github.com/airbytehq/airbyte/issues/1978
     Problem described here https://github.com/formium/formik/issues/445
     The problem is next:
     
     When we touch the field, it would be set as touched field correctly.
     If validation fails on submit - Formik detects touched object mapping based
     either on initialValues passed to Formik or on current value set.
     So in case of creation, if we touch an input, don't change value and 
     press submit - our touched map will be cleared. 
     
     This hack just touches all fields on submit.
   */
  useEffect(() => {
    if (isSubmitting && !isValidating) {
      for (const path of Object.keys(flatten(errors))) {
        setFieldTouched(path, true, false);
      }
    }
  }, [errors, isSubmitting, isValidating, setFieldTouched]);
};

export {
  useBuildForm,
  useBuildUiWidgets,
  useConstructValidationSchema,
  usePatchFormik,
};
