import { JSONSchema7Definition } from "json-schema";

import { NamespaceDefinitionType } from "../../request/AirbyteClient";
import { SOURCE_NAMESPACE_TAG } from "../connector/source";
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
  namespaceDefinition: typeof NamespaceDefinitionType.source | typeof NamespaceDefinitionType.destination;
  sourceNamespace?: string;
}
interface NamespaceOptionsCustomFormat {
  namespaceDefinition: typeof NamespaceDefinitionType.customformat;
  namespaceFormat: string;
  sourceNamespace?: string;
}

function getDestinationNamespace(opt: NamespaceOptions | NamespaceOptionsCustomFormat) {
  const destinationSetting = "<destination schema>";
  switch (opt.namespaceDefinition) {
    case NamespaceDefinitionType.source:
      return opt.sourceNamespace ?? destinationSetting;
    case NamespaceDefinitionType.destination:
      return destinationSetting;
    case NamespaceDefinitionType.customformat:
    default: // Default is never hit, but typescript prefers it declared
      if (!opt.sourceNamespace?.trim()) {
        return destinationSetting;
      }
      return opt.namespaceFormat.replace(SOURCE_NAMESPACE_TAG, opt.sourceNamespace);
  }
}

export { getDestinationNamespace, traverseSchemaToField };
