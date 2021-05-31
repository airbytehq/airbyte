import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

export function isSourceDefinition(
  item: SourceDefinition | DestinationDefinition
): item is SourceDefinition {
  return (item as SourceDefinition).sourceDefinitionId !== undefined;
}
