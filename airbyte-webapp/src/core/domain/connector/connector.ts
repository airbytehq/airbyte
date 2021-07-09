import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

export function isConnectorDeprecated(
  item: SourceDefinition | DestinationDefinition
): boolean {
  return !item.latestDockerImageTag;
}
