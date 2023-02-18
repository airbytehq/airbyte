import { NamespaceDefinitionType } from "core/request/AirbyteClient";

export const namespaceDefinitionOptions = {
  [NamespaceDefinitionType.destination]: "destinationFormat",
  [NamespaceDefinitionType.source]: "sourceFormat",
  [NamespaceDefinitionType.customformat]: "customFormat",
};
