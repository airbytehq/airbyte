import * as yup from "yup";
import { useCallback, useMemo, useState } from "react";
import { JSONSchema6 } from "json-schema";
import merge from "lodash.merge";

import {
  FormBlock,
  WidgetConfig,
  WidgetConfigMap
} from "../../core/form/types";
import { jsonSchemaToUiWidget } from "../../core/jsonSchema/schemaToUiWidget";
import { buildYupFormForJsonSchema } from "../../core/jsonSchema/schemaToYup";
import { buildPathInitialState } from "../../core/form/uiWidget";

export type FormInitialValues = {
  name: string;
  serviceType: string;
  frequency?: string;
  connectionConfiguration?: any;
};

export const useConstructValidationSchema = (
  uiWidgetsInfo: WidgetConfigMap,
  jsonSchema?: JSONSchema6
) => {
  return useMemo(() => {
    let validationShape: yup.ObjectSchema<any> = yup.object().shape({
      name: yup.string().required("form.empty.error"),
      serviceType: yup.string().required("form.empty.error")
    });

    // We have additional fields. Lets build schema for them
    if (jsonSchema?.properties) {
      validationShape = validationShape.shape({
        connectionConfiguration: buildYupFormForJsonSchema(
          jsonSchema,
          uiWidgetsInfo
        )
      });
    }

    return validationShape;
  }, [uiWidgetsInfo, jsonSchema]);
};

export function useBuildForm(
  formType: "connection" | "source" | "destination",
  isLoading?: boolean,
  initialValues?: Partial<FormInitialValues>,
  jsonSchema?: JSONSchema6
): {
  initialValues: FormInitialValues;
  formFields: FormBlock[];
} {
  const startValues = useMemo<FormInitialValues>(() => {
    const initVals: FormInitialValues = { name: "", serviceType: "" };

    if (formType === "connection") {
      initVals["frequency"] = "";
    }

    const values: FormInitialValues = {
      ...initVals,
      ...initialValues
    };

    return values;
  }, [formType, initialValues]);

  const formFields = useMemo<FormBlock[]>(() => {
    return [
      {
        _type: "formItem",
        type: "string",
        fieldKey: "name",
        fieldName: "name",
        isRequired: true
      },
      {
        _type: "formItem",
        type: "string",
        fieldKey: "serviceType",
        fieldName: "serviceType",
        // TODO: find better approach and possibly move to UIWidget
        meta: {
          includeInstruction: formType !== "connection"
        },
        isRequired: true
      },
      ...(jsonSchema && !isLoading
        ? [jsonSchemaToUiWidget(jsonSchema, "connectionConfiguration")]
        : []),
      ...((formType === "connection"
        ? [
            {
              _type: "formItem",
              fieldKey: "frequency",
              fieldName: "frequency",
              type: "string",
              isRequired: true
            }
          ]
        : []) as FormBlock[])
    ];
  }, [jsonSchema, isLoading, formType]);

  return {
    initialValues: startValues,
    formFields
  };
}

export const useBuildUiWidgets = (
  formFields: FormBlock[],
  formValues: FormInitialValues
) => {
  const initialUiWidgetsState = useMemo(
    () => buildPathInitialState(formFields, formValues, {}),
    [formFields, formValues]
  );

  const [uiWidgetsInfo, setUiWidgetsInfo] = useState(initialUiWidgetsState);

  const setUiWidgetsInfoSubState = useCallback(
    (widgetId: string, updatedValues: WidgetConfig) =>
      setUiWidgetsInfo({ ...uiWidgetsInfo, [widgetId]: updatedValues }),
    [uiWidgetsInfo, setUiWidgetsInfo]
  );

  // As schema is dynamic, it is possible, that new updated values, will differ from one stored.
  const mergedState = useMemo(
    () => merge(initialUiWidgetsState, uiWidgetsInfo),
    [initialUiWidgetsState, uiWidgetsInfo]
  );

  return {
    uiWidgetsInfo: mergedState,
    setUiWidgetsInfo: setUiWidgetsInfoSubState
  };
};
