import flatten from "flat";
import { useFormikContext } from "formik";
import { JSONSchema7, JSONSchema7Definition } from "json-schema";
import merge from "lodash/merge";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AnySchema } from "yup";

import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { FormBlock, WidgetConfig, WidgetConfigMap } from "core/form/types";
import { buildPathInitialState } from "core/form/uiWidget";
import { applyFuncAt, removeNestedPaths } from "core/jsonSchema";
import { jsonSchemaToUiWidget } from "core/jsonSchema/schemaToUiWidget";
import { buildYupFormForJsonSchema } from "core/jsonSchema/schemaToYup";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import { DestinationDefinitionSpecificationRead } from "../../../core/request/AirbyteClient";
import { ServiceFormValues } from "./types";

function upgradeSchemaLegacyAuth(
  connectorSpecification: Required<
    Pick<DestinationDefinitionSpecificationRead, "authSpecification" | "connectionSpecification">
  >
) {
  const spec = connectorSpecification.authSpecification.oauth2Specification;
  return applyFuncAt(
    connectorSpecification.connectionSpecification as JSONSchema7Definition,
    (spec?.rootObject ?? []) as Array<string | number>,
    (schema) => {
      // Very hacky way to allow placing button within section
      // @ts-expect-error json schema
      schema.is_auth = true;
      const schemaWithoutPaths = removeNestedPaths(schema, spec?.oauthFlowInitParameters ?? [], false);

      const schemaWithoutOutputPats = removeNestedPaths(
        schemaWithoutPaths,
        spec?.oauthFlowOutputParameters ?? [],
        false
      );

      return schemaWithoutOutputPats;
    }
  );
}

export function useBuildInitialSchema(
  connectorSpecification?: ConnectorDefinitionSpecification
): JSONSchema7Definition | undefined {
  const allowOAuthConnector = useFeature(FeatureItem.AllowOAuthConnector);

  return useMemo(() => {
    if (allowOAuthConnector) {
      if (connectorSpecification?.authSpecification && !connectorSpecification?.advancedAuth) {
        return upgradeSchemaLegacyAuth({
          connectionSpecification: connectorSpecification?.connectionSpecification,
          authSpecification: connectorSpecification.authSpecification,
        });
      }
    }

    return connectorSpecification?.connectionSpecification as JSONSchema7Definition | undefined;
  }, [allowOAuthConnector, connectorSpecification]);
}

export interface BuildFormHook {
  initialValues: ServiceFormValues;
  formFields: FormBlock;
}

export function useBuildForm(jsonSchema: JSONSchema7, initialValues?: Partial<ServiceFormValues>): BuildFormHook {
  const startValues = useMemo<ServiceFormValues>(
    () => ({
      name: "",
      serviceType: "",
      connectionConfiguration: {},
      ...initialValues,
    }),
    [initialValues]
  );

  const formFields = useMemo<FormBlock>(() => jsonSchemaToUiWidget(jsonSchema), [jsonSchema]);

  return {
    initialValues: startValues,
    formFields,
  };
}

interface BuildUiWidgetsContextHook {
  uiWidgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (widgetId: string, updatedValues: WidgetConfig) => void;
  resetUiWidgetsInfo: () => void;
}

export const useBuildUiWidgetsContext = (
  formFields: FormBlock[] | FormBlock,
  formValues: ServiceFormValues,
  uiOverrides?: WidgetConfigMap
): BuildUiWidgetsContextHook => {
  const [overriddenWidgetState, setUiWidgetsInfo] = useState<WidgetConfigMap>(uiOverrides ?? {});

  // As schema is dynamic, it is possible, that new updated values, will differ from one stored.
  const mergedState = useMemo(
    () =>
      merge(
        buildPathInitialState(Array.isArray(formFields) ? formFields : [formFields], formValues),
        merge(overriddenWidgetState, uiOverrides)
      ),
    [formFields, formValues, overriddenWidgetState, uiOverrides]
  );

  const setUiWidgetsInfoSubState = useCallback(
    (widgetId: string, updatedValues: WidgetConfig) => setUiWidgetsInfo({ ...mergedState, [widgetId]: updatedValues }),
    [mergedState, setUiWidgetsInfo]
  );

  const resetUiWidgetsInfo = useCallback(() => {
    setUiWidgetsInfo(uiOverrides ?? {});
  }, [uiOverrides]);

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
