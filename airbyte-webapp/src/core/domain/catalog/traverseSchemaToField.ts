import { JSONSchema7Definition } from "json-schema";

import { SyncSchemaField } from "./models";

type AirbyteJsonSchema = JSONSchema7Definition & {
  airbyte_type?: string;
  $ref?: string;
};

export const traverseSchemaToField = (
  jsonSchema: AirbyteJsonSchema | undefined,
  key: string | undefined
): SyncSchemaField[] => {
  // For the top level we should not insert an extra object
  return traverseJsonSchemaProperties(jsonSchema, key)[0].fields ?? [];
};

const traverseJsonSchemaProperties = (
  jsonSchema: AirbyteJsonSchema | undefined,
  key: string | undefined = "",
  path: string[] = []
): SyncSchemaField[] => {
  if (typeof jsonSchema === "boolean") {
    return [];
  }

  let fields: SyncSchemaField[] | undefined;
  if (jsonSchema?.properties) {
    fields = Object.entries(jsonSchema.properties)
      .flatMap(([k, schema]) => traverseJsonSchemaProperties(schema, k, [...path, k]))
      .flat(2);
  }

  return [
    {
      cleanedName: key,
      path,
      key,
      fields,
      type:
        (Array.isArray(jsonSchema?.type)
          ? jsonSchema?.type.find((t) => t !== "null") ?? jsonSchema?.type[0]
          : jsonSchema?.type) ?? "null",
      $ref: jsonSchema?.$ref,
      airbyte_type: jsonSchema?.airbyte_type,
      format: jsonSchema?.format,
    },
  ];
};
