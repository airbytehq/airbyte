import { JSONSchema7Definition } from "json-schema";

import { NamespaceDefinitionType } from "../../request/AirbyteClient";
import { SyncSchemaField } from "./models";

type AirbyteJsonSchema = JSONSchema7Definition & {
  airbyte_type?: string;
};

const traverseSchemaToField = (
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
      airbyte_type: jsonSchema?.airbyte_type,
      format: jsonSchema?.format,
    },
  ];
};

interface NamespaceOptions {
  namespaceDefinition:
    | typeof NamespaceDefinitionType.source
    | typeof NamespaceDefinitionType.destination
    | typeof NamespaceDefinitionType.customformat;
  namespaceFormat?: string;
}

function getDestinationNamespace(opt: NamespaceOptions) {
  switch (opt.namespaceDefinition) {
    case NamespaceDefinitionType.source:
      return "<source schema>";
    case NamespaceDefinitionType.destination:
      return "<destination schema>";
    case NamespaceDefinitionType.customformat:
      return opt.namespaceFormat;
  }
}

export { getDestinationNamespace, traverseSchemaToField };
