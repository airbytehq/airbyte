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
  key = "",
  path: string = key,
  parentSchema?: JSONSchema7Definition
): FormBlock => {
  const isRequired = isKeyRequired(key, parentSchema);

  // TODO: decide what to do with boolean case
  if (typeof jsonSchema === "boolean") {
    return {
      _type: "formItem",
      path: key,
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
      path: path || key,
      fieldKey: key,
      conditions,
      isRequired,
    };
  }

  if (
    jsonSchema.type === "array" &&
    typeof jsonSchema.items === "object" &&
    !Array.isArray(jsonSchema.items) &&
    jsonSchema.items.type === "object"
  ) {
    return {
      ...pickDefaultFields(jsonSchema),
      _type: "objectArray",
      path: path || key,
      fieldKey: key,
      properties: jsonSchemaToUiWidget(jsonSchema.items, key, path),
      isRequired,
    };
  }

  if (jsonSchema.properties) {
    const properties = Object.entries(
      jsonSchema.properties
    ).map(([k, schema]) =>
      jsonSchemaToUiWidget(schema, k, path ? `${path}.${k}` : k, jsonSchema)
    );

    return {
      ...pickDefaultFields(jsonSchema),
      _type: "formGroup",
      jsonSchema,
      path: path || key,
      fieldKey: key,
      properties,
      isRequired,
    };
  }

  return {
    ...pickDefaultFields(jsonSchema),
    _type: "formItem",
    path: path || key,
    fieldKey: key,
    isRequired,
    isSecret: (jsonSchema as { airbyte_secret: boolean }).airbyte_secret,
    multiline: (jsonSchema as { multiline: boolean }).multiline,
    type:
      (Array.isArray(jsonSchema.type) ? jsonSchema.type[0] : jsonSchema.type) ??
      "null",
  };
};

function isKeyRequired(
  key: string,
  parentSchema?: JSONSchema7Definition
): boolean {
  const isRequired =
    (typeof parentSchema !== "boolean" &&
      Array.isArray(parentSchema?.required) &&
      parentSchema?.required.includes(key)) ||
    false;

  return isRequired;
}

const pickDefaultFields = (schema: JSONSchema7): Partial<JSONSchema7> => ({
  default: schema.default,
  examples: schema.examples,
  description: schema.description,
  pattern: schema.pattern,
  title: schema.title,
  enum:
    typeof schema.items === "object" &&
    !Array.isArray(schema.items) &&
    schema.items.enum
      ? schema.items.enum
      : schema.enum,
});
