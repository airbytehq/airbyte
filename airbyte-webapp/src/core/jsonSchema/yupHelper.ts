import { JSONSchema6 } from "json-schema";
import * as yup from "yup";
import { WidgetConfigMap } from "../form/types";

export const buildYupFormForJsonSchema = (
  jsonSchema: JSONSchema6,
  uiConfig?: WidgetConfigMap,
  parentSchema?: JSONSchema6,
  propertyKey?: string
): yup.Schema<any> => {
  let schema:
    | yup.NumberSchema
    | yup.StringSchema
    | yup.ObjectSchema
    | null = null;

  if (jsonSchema.oneOf && uiConfig && propertyKey) {
    const selectedSchema =
      jsonSchema.oneOf.find(condition => {
        if (typeof condition !== "boolean") {
          return uiConfig[propertyKey]?.selectedItem === condition.title;
        }
        return false;
      }) ?? jsonSchema.oneOf[0];
    if (selectedSchema && typeof selectedSchema !== "boolean") {
      return buildYupFormForJsonSchema(
        { type: jsonSchema.type, ...selectedSchema },
        uiConfig,
        jsonSchema,
        propertyKey
      );
    }
  }

  switch (jsonSchema.type) {
    case "string":
      schema = yup.string();
      break;
    case "integer":
      schema = yup.number();

      if (jsonSchema?.minimum !== undefined) {
        schema = schema.min(jsonSchema?.minimum);
      }

      if (jsonSchema?.maximum !== undefined) {
        schema = schema!.max(jsonSchema?.maximum);
      }
      break;
    case "object":
      schema = yup
        .object()
        .shape(
          Object.fromEntries(
            Object.entries(
              jsonSchema.properties || {}
            ).map(([propertyKey, condition]) => [
              propertyKey,
              typeof condition !== "boolean"
                ? buildYupFormForJsonSchema(
                    condition,
                    uiConfig,
                    jsonSchema,
                    propertyKey
                  )
                : yup.mixed()
            ])
          )
        );
  }

  const isRequired =
    !jsonSchema?.default &&
    parentSchema &&
    Array.isArray(parentSchema?.required) &&
    parentSchema.required.find(item => item === propertyKey);

  if (isRequired && schema) {
    schema = schema.required("form.empty.error");
  }

  return schema || yup.mixed();
};
