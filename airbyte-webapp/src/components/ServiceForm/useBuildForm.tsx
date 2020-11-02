import * as yup from "yup";
import { useMemo } from "react";
import { JSONSchema6 } from "json-schema";

import { FormBlock } from "../../core/form/types";
import { jsonSchemaToUiWidget } from "../../core/jsonSchema/uiWidget";
import { buildYupFormForJsonSchema } from "../../core/jsonSchema/yupHelper";

export type FormInitialValues = {
  name: string;
  serviceType: string;
  frequency?: string;
  connectionConfiguration?: any;
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
  }, [jsonSchema]);

  const validationSchema = useConstructValidationSchema(jsonSchema);

  return {
    initialValues: startValues,
    formFields,
    validationSchema
  };
}

const useConstructValidationSchema = (jsonSchema?: JSONSchema6) => {
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

  return useMemo(() => validationShape, [jsonSchema]);
};

export default useConstructValidationSchema;
