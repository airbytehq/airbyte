import { ConnectorDefinition, DestinationDefinition } from "./types";

export function isDestinationDefinition(connector: ConnectorDefinition): connector is DestinationDefinition {
  return (connector as DestinationDefinition).destinationDefinitionId !== undefined;
}
