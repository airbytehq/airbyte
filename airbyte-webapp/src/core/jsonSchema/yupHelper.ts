import { JSONSchema6 } from "json-schema";
import * as yup from "yup";

export const buildYupFormForJsonSchema = (jsonSchema: JSONSchema6) => {
  return yup.object().shape(
    Object.keys(jsonSchema.properties || {}).reduce<{
      [key: string]: any;
    }>((acc, propertyKey) => {
      const condition = jsonSchema?.properties?.[propertyKey];

      if (!condition || typeof condition === "boolean") {
        return acc;
      }

      let schema = null;

      switch (condition?.type) {
        case "string":
          schema = yup.string();
          break;
        case "integer":
          schema = yup.number();

          if (condition?.minimum) {
            schema = schema.min(condition?.minimum);
          }

          if (condition?.maximum) {
            schema = schema.max(condition?.maximum);
          }
          break;
      }

      const isRequired =
        !condition?.default &&
        Array.isArray(jsonSchema.required) &&
        jsonSchema.required.find(item => item === propertyKey);

      if (isRequired && schema) {
        schema = schema.required("form.empty.error");
      }

      acc[propertyKey] = schema;

      return acc;
    }, {})
  );
};
