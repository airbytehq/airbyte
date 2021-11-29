import { ConnectorDefinition } from "./types";
import { DestinationDefinition } from "../../resources/DestinationDefinition";

export function isDestinationDefinition(
  connector: ConnectorDefinition
): connector is DestinationDefinition {
  return (
    (connector as DestinationDefinition).destinationDefinitionId !== undefined
  );
}
