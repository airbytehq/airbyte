import { NamespaceDefinitionType } from "core/request/AirbyteClient";

export const namespaceDefinitionOptions: Record<NamespaceDefinitionType, string> = {
  [NamespaceDefinitionType.destination]: "destinationFormat",
  [NamespaceDefinitionType.source]: "sourceFormat",
  [NamespaceDefinitionType.customformat]: "customFormat",
};
