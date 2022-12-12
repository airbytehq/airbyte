import flatten from "flat";
import { useFormikContext } from "formik";
import { JSONSchema7, JSONSchema7Definition } from "json-schema";
import merge from "lodash/merge";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { AnySchema } from "yup";

import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { FormBlock, WidgetConfig, WidgetConfigMap } from "core/form/types";
import { buildPathInitialState } from "core/form/uiWidget";
import { jsonSchemaToUiWidget } from "core/jsonSchema/schemaToUiWidget";
import { buildYupFormForJsonSchema } from "core/jsonSchema/schemaToYup";

import { ConnectorFormValues } from "./types";

export interface BuildFormHook {
  initialValues: ConnectorFormValues;
  formFields: FormBlock;
  jsonSchema: JSONSchema7;
}

export function useBuildForm(
  formType: "source" | "destination",
  selectedConnectorDefinitionSpecification: ConnectorDefinitionSpecification,
  initialValues?: Partial<ConnectorFormValues>
): BuildFormHook {
  const { formatMessage } = useIntl();

  const jsonSchema: JSONSchema7 = useMemo(
    () => ({
      type: "object",
      properties: {
        name: {
          type: "string",
          title: formatMessage({ id: `form.${formType}Name` }),
          description: formatMessage({ id: `form.${formType}Name.message` }),
        },
        connectionConfiguration:
          selectedConnectorDefinitionSpecification.connectionSpecification as JSONSchema7Definition,
      },
      required: ["name"],
    }),
    [formType, formatMessage, selectedConnectorDefinitionSpecification.connectionSpecification]
  );
  const startValues = useMemo<ConnectorFormValues>(
    () => ({
      name: "",
      connectionConfiguration: {},
      ...initialValues,
    }),
    [initialValues]
  );

  const formFields = useMemo<FormBlock>(() => jsonSchemaToUiWidget(jsonSchema), [jsonSchema]);

  return {
    initialValues: startValues,
    formFields,
    jsonSchema,
  };
}

// useBuildUiWidgetsContext hook
interface BuildUiWidgetsContextHook {
  uiWidgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (widgetId: string, updatedValues: WidgetConfig) => void;
  resetUiWidgetsInfo: () => void;
}

export const useBuildUiWidgetsContext = (
  formFields: FormBlock[] | FormBlock,
  formValues: ConnectorFormValues
): BuildUiWidgetsContextHook => {
  const [overriddenWidgetState, setUiWidgetsInfo] = useState<WidgetConfigMap>({});

  // As schema is dynamic, it is possible, that new updated values, will differ from one stored.
  const mergedState = useMemo(
    () =>
      merge(
        buildPathInitialState(Array.isArray(formFields) ? formFields : [formFields], formValues),
        merge(overriddenWidgetState)
      ),
    [formFields, formValues, overriddenWidgetState]
  );

  const setUiWidgetsInfoSubState = useCallback(
    (widgetId: string, updatedValues: WidgetConfig) => setUiWidgetsInfo({ ...mergedState, [widgetId]: updatedValues }),
    [mergedState, setUiWidgetsInfo]
  );

  const resetUiWidgetsInfo = useCallback(() => {
    setUiWidgetsInfo({});
  }, []);

  return {
    uiWidgetsInfo: mergedState,
    setUiWidgetsInfo: setUiWidgetsInfoSubState,
    resetUiWidgetsInfo,
  };
};

// As validation schema depends on what path of oneOf is currently selected in jsonschema
export const useConstructValidationSchema = (jsonSchema: JSONSchema7, uiWidgetsInfo: WidgetConfigMap): AnySchema =>
  useMemo(() => buildYupFormForJsonSchema(jsonSchema, uiWidgetsInfo), [uiWidgetsInfo, jsonSchema]);

export const usePatchFormik = (): void => {
  const { setFieldTouched, isSubmitting, isValidating, errors } = useFormikContext();

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
