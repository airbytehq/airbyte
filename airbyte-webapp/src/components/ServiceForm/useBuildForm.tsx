import * as yup from "yup";
import { useCallback, useMemo, useState } from "react";
import { JSONSchema6 } from "json-schema";
import at from "lodash.at";

import { FormBlock } from "../../core/form/types";
import { jsonSchemaToUiWidget } from "../../core/jsonSchema/uiWidget";
import { buildYupFormForJsonSchema } from "../../core/jsonSchema/yupHelper";

export type WidgetConfig = { [key: string]: any };

export type FormInitialValues = {
  name: string;
  serviceType: string;
  frequency?: string;
  connectionConfiguration?: any;
};

const useConstructValidationSchema = (jsonSchema?: JSONSchema6) => {
  return useMemo(() => {
    let validationShape: yup.ObjectSchema<any> = yup.object().shape({
      name: yup.string().required("form.empty.error"),
      serviceType: yup.string().required("form.empty.error")
    });

    // We have additional fields. Lets build schema for them
    if (jsonSchema?.properties) {
      validationShape = validationShape.shape({
        connectionConfiguration: buildYupFormForJsonSchema(jsonSchema)
      });
    }

    return validationShape;
  }, [jsonSchema]);
};

export function useBuildForm(
  initialValues: Partial<FormInitialValues>,
  formType: "connection" | "source" | "destination",
  jsonSchema?: JSONSchema6
): {
  initialValues: FormInitialValues;
  formFields: FormBlock[];
  validationSchema: yup.ObjectSchema;
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
  }, [formType]);

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
        isRequired: true,
        // TODO: move to UI widget config
        meta: {
          includeInstruction: formType !== "connection"
        }
      },
      ...(jsonSchema
        ? [jsonSchemaToUiWidget(jsonSchema, "connectionConfiguration")]
        : []),
      ...((formType === "connection"
        ? [
            {
              _type: "formItem",
              fieldKey: "frequency",
              fieldName: "frequency",
              type: "array",
              isRequired: true
            }
          ]
        : []) as FormBlock[])
    ];
  }, [jsonSchema, formType]);

  const validationSchema = useConstructValidationSchema(jsonSchema);

  return {
    initialValues: startValues,
    formFields,
    validationSchema
  };
}

const buildPathInitialState = (
  formBlock: FormBlock[],
  formValues: FormInitialValues,
  widgetState: { [key: string]: WidgetConfig }
): { [key: string]: WidgetConfig } =>
  formBlock.reduce((widgetStateBuilder, formItem) => {
    switch (formItem._type) {
      case "formGroup":
        return buildPathInitialState(
          formItem.properties,
          formValues,
          widgetStateBuilder
        );
      case "formItem":
        break;
      case "formCondition":
        const defaultCondition = Object.entries(formItem.conditions).find(
          ([, subConditionItems]) => {
            switch (subConditionItems._type) {
              case "formGroup":
                return subConditionItems.properties.every(
                  p => at(formValues, p.fieldName) !== undefined
                );
              case "formItem":
                return at(formValues, subConditionItems.fieldName);
            }
            return false;
          }
        )?.[0];

        const selectedPath =
          defaultCondition ?? Object.keys(formItem.conditions)?.[0];
        widgetStateBuilder[formItem.fieldName] = {
          selectedItem: selectedPath
        };
        if (formItem.conditions[selectedPath]) {
          return buildPathInitialState(
            [formItem.conditions[selectedPath]],
            formValues,
            widgetStateBuilder
          );
        }
    }

    return widgetStateBuilder;
  }, widgetState);

export const useBuildUiWidgets = (
  formFields: FormBlock[],
  formValues: FormInitialValues
  // defaultConfig?: { [key: string]: object }
) => {
  const initialUiWidgetsState = useMemo(() => {
    return buildPathInitialState(formFields, formValues, {});
  }, [formFields]);

  const [uiWidgetsInfo, setUiWidgetsInfo] = useState(initialUiWidgetsState);

  const setUiWidgetsInfoSubState = useCallback(
    (widgetId: string, updatedValues: WidgetConfig) =>
      setUiWidgetsInfo({ ...uiWidgetsInfo, [widgetId]: updatedValues }),
    [setUiWidgetsInfo]
  );

  return {
    uiWidgetsInfo,
    setUiWidgetsInfo: setUiWidgetsInfoSubState
  };
};
