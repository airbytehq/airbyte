import { JSONSchema7, JSONSchema7Definition } from "json-schema";

import { FormBlock } from "core/form/types";

/**
 * Returns {@link FormBlock} representation of jsonSchema
 *
 * Builds internal {@link FormBlock} from jsonSchema recursively.
 * Allows to walk through and validate schema in a more convenient way
 *
 * @param jsonSchema
 * @param key
 * @param path
 * @param parentSchema
 */
export const jsonSchemaToUiWidget = (
  jsonSchema: JSONSchema7Definition,
  key: string,
  path: string = key,
  parentSchema?: JSONSchema7Definition
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
      type: "null",
      isRequired,
      isSecret: false,
    };
  }

  if (jsonSchema.oneOf?.length && jsonSchema.oneOf.length > 0) {
    const conditions = Object.fromEntries(
      jsonSchema.oneOf.map((condition) => {
        if (typeof condition === "boolean") {
          return [];
        }
        return [condition.title, jsonSchemaToUiWidget(condition, key, path)];
      })
    );

    return {
      _type: "formCondition",
      fieldName: path || key,
      fieldKey: key,
      conditions,
      isRequired,
    };
  }

  if (jsonSchema.properties) {
    const properties = Object.entries(
      jsonSchema.properties
    ).map(([k, schema]) =>
      jsonSchemaToUiWidget(schema, k, `${path}.${k}`, jsonSchema)
    );

    return {
      ...pickDefaultFields(jsonSchema),
      _type: "formGroup",
      fieldName: path || key,
      fieldKey: key,
      properties,
      isRequired,
    };
  }

  return {
    ...pickDefaultFields(jsonSchema),
    _type: "formItem",
    fieldName: path || key,
    fieldKey: key,
    isRequired,
    isSecret: (jsonSchema as { airbyte_secret: boolean }).airbyte_secret,
    type:
      (Array.isArray(jsonSchema.type) ? jsonSchema.type[0] : jsonSchema.type) ??
      "null",
  };
};

const pickDefaultFields = (schema: JSONSchema7): Partial<JSONSchema7> => ({
  default: schema.default,
  examples: schema.examples,
  description: schema.description,
  pattern: schema.pattern,
  title: schema.title,
  enum: schema.enum,
});
