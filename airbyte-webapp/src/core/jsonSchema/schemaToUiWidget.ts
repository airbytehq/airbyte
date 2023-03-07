import pick from "lodash/pick";

import { FormBlock } from "core/form/types";
import { isDefined } from "utils/common";

import { AirbyteJSONSchemaDefinition, AirbyteJSONSchema } from "./types";

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
  jsonSchema: AirbyteJSONSchemaDefinition,
  key = "",
  path: string = key,
  parentSchema?: AirbyteJSONSchemaDefinition
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
        return [condition.title, jsonSchemaToUiWidget({ ...condition, type: jsonSchema.type }, key, path)];
      })
    );

    return {
      ...pickDefaultFields(jsonSchema),
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

  if (jsonSchema.type === "object") {
    const properties = Object.entries(jsonSchema.properties || []).map(([k, schema]) =>
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
    isSecret: !!jsonSchema.airbyte_secret,
    multiline: !!jsonSchema.multiline,
    format: jsonSchema.format,
    type: (Array.isArray(jsonSchema.type) ? jsonSchema.type[0] : jsonSchema.type) ?? "null",
  };
};

function isKeyRequired(key: string, parentSchema?: AirbyteJSONSchemaDefinition): boolean {
  const isRequired =
    (typeof parentSchema !== "boolean" &&
      Array.isArray(parentSchema?.required) &&
      parentSchema?.required.includes(key)) ||
    false;

  return isRequired;
}

const defaultFields = [
  "default",
  "examples",
  "description",
  "pattern",
  "order",
  "const",
  "title",
  "enum",

  // airbyte specific fields
  "airbyte_hidden",
] as const;

const pickDefaultFields = (schema: AirbyteJSONSchema) => {
  const partialSchema = pick(schema, defaultFields);

  if (typeof schema.items === "object" && !Array.isArray(schema.items) && schema.items.enum) {
    partialSchema.enum = schema.items.enum;
  } else if (schema.enum && schema.enum?.length === 1 && isDefined(schema.default)) {
    partialSchema.const = schema.default;
    // remove enum key as it has been "picked" already above
    delete partialSchema.enum;
  }

  return partialSchema;
};
