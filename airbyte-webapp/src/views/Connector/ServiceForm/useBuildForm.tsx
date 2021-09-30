import { AnySchema } from "yup";
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
import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { useFeatureService } from "hooks/services/Feature";
import { applyFuncAt, removeNestedPaths } from "core/jsonSchema";

function useBuildInitialSchema(
  connectorSpecification?: ConnectorDefinitionSpecification
): JSONSchema7 | undefined {
  const { hasFeature } = useFeatureService();

  return useMemo(() => {
    if (
      hasFeature("ALLOW_OAUTH_CONNECTOR") &&
      connectorSpecification?.authSpecification
    ) {
      const spec = connectorSpecification.authSpecification.oauth2Specification;
      return applyFuncAt(
        connectorSpecification.connectionSpecification,
        spec.rootObject ?? [],
        (schema) => {
          // Very hacky way to allow placing button within section
          (schema as any).is_auth = true;
          const schemaWithoutPaths = removeNestedPaths(
            schema,
            spec.oauthFlowInitParameters ?? []
          );

          const schemaWithoutOutputPats = removeNestedPaths(
            schemaWithoutPaths,
            spec.oauthFlowOutputParameters ?? [],
            false
          );

          return schemaWithoutOutputPats;
        }
      );
    }

    return connectorSpecification?.connectionSpecification;
  }, [hasFeature, connectorSpecification]);
}

function useBuildForm(
  jsonSchema: JSONSchema7,
  initialValues?: Partial<ServiceFormValues>
): {
  initialValues: ServiceFormValues;
  formFields: FormBlock;
} {
  const startValues = useMemo<ServiceFormValues>(
    () => ({
      name: "",
      serviceType: "",
      connectionConfiguration: {},
      ...initialValues,
    }),
    [initialValues]
  );

  const formFields = useMemo<FormBlock>(
    () => jsonSchemaToUiWidget(jsonSchema),
    [jsonSchema]
  );

  return {
    initialValues: startValues,
    formFields,
  };
}

const useBuildUiWidgets = (
  formFields: FormBlock[] | FormBlock,
  formValues: ServiceFormValues,
  uiOverrides?: WidgetConfigMap
): {
  uiWidgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (widgetId: string, updatedValues: WidgetConfig) => void;
} => {
  const [overriddenWidgetState, setUiWidgetsInfo] = useState<WidgetConfigMap>(
    uiOverrides ?? {}
  );

  // As schema is dynamic, it is possible, that new updated values, will differ from one stored.
  const mergedState = useMemo(
    () =>
      merge(
        buildPathInitialState(
          Array.isArray(formFields) ? formFields : [formFields],
          formValues
        ),
        merge(overriddenWidgetState, uiOverrides)
      ),
    [formFields, formValues, overriddenWidgetState, uiOverrides]
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
  jsonSchema: JSONSchema7
): AnySchema =>
  useMemo(() => buildYupFormForJsonSchema(jsonSchema, uiWidgetsInfo), [
    uiWidgetsInfo,
    jsonSchema,
  ]);

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
  useBuildInitialSchema,
  useBuildUiWidgets,
  useConstructValidationSchema,
  usePatchFormik,
};
