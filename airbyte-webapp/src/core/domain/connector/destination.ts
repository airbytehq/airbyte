import { DestinationDefinitionRead } from "core/request/AirbyteClient";

import { ConnectorDefinition } from "./types";

export function isDestinationDefinition(connector: ConnectorDefinition): connector is DestinationDefinitionRead {
  return (connector as DestinationDefinitionRead).destinationDefinitionId !== undefined;
}
