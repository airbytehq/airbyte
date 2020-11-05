import { JSONSchema6Definition } from "json-schema";
import pick from "lodash.pick";

import { FormBlock } from "../form/types";

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
  jsonSchema: JSONSchema6Definition,
  key: string,
  path: string = key,
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

  if (jsonSchema.oneOf?.length && jsonSchema.oneOf.length > 0) {
    const conditions = Object.fromEntries(
      jsonSchema.oneOf.map(condition => {
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
      isRequired
    };
  }

  if (jsonSchema.properties) {
    const properties = Object.entries(
      jsonSchema.properties
    ).map(([k, schema]) =>
      jsonSchemaToUiWidget(schema, k, `${path}.${k}`, jsonSchema)
    );

    return {
      ...pick(jsonSchema, [
        "default",
        "examples",
        "description",
        "title",
        "enum"
      ]),
      _type: "formGroup",
      fieldName: path || key,
      fieldKey: key,
      properties,
      isRequired
    };
  }

  return {
    ...pick(jsonSchema, [
      "default",
      "examples",
      "description",
      "title",
      "enum"
    ]),
    _type: "formItem",
    fieldName: path || key,
    fieldKey: key,
    isRequired,
    type:
      (Array.isArray(jsonSchema.type) ? jsonSchema.type[0] : jsonSchema.type) ??
      "any"
  };
};
