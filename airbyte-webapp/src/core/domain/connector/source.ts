import { SourceDefinition } from "core/resources/SourceDefinition";
import { ConnectorDefinition } from "./connector";

export function isSourceDefinition(
  connector: ConnectorDefinition
): connector is SourceDefinition {
  return (connector as SourceDefinition).sourceDefinitionId !== undefined;
}
