import { JSONSchema6Definition } from "json-schema";
import { FormBlock } from "../form/types";

export const jsonSchemaToUiWidget = (
  jsonSchema: JSONSchema6Definition,
  key: string,
  path?: string,
  parentSchema?: JSONSchema6Definition
): FormBlock => {
  const isRequired =
    (typeof parentSchema !== "boolean" &&
      Array.isArray(parentSchema?.required) &&
      parentSchema?.required.includes(key)) ||
    false;

  // TODO: decide what to do with boolean case
  if (typeof jsonSchema === "boolean") {
    return {
      _type: "formItem",
      fieldName: key,
      fieldKey: key,
      type: "any",
      isRequired
    };
  }

  if (jsonSchema.properties) {
    const properties = Object.entries(
      jsonSchema.properties
    ).map(([k, schema]) =>
      jsonSchemaToUiWidget(schema, k, `${key}.${k}`, jsonSchema)
    );

    return {
      default: jsonSchema.default,
      examples: jsonSchema.examples,
      description: jsonSchema.description,
      _type: "formGroup",
      fieldName: path || key,
      fieldKey: key,
      properties,
      isRequired
    };
  }

  return {
    title: jsonSchema.title,
    default: jsonSchema.default,
    examples: jsonSchema.examples,
    description: jsonSchema.description,
    fieldName: path || key,
    fieldKey: key,
    isRequired,
    type:
      (Array.isArray(jsonSchema.type) ? jsonSchema.type[0] : jsonSchema.type) ??
      "any",
    _type: "formItem"
  };
};
