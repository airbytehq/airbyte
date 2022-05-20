import { DestinationDefinitionRead, DestinationDefinitionSpecificationRead } from "core/request/AirbyteClient";

import { ConnectorDefinition, ConnectorDefinitionSpecification } from "./types";

export function isDestinationDefinition(connector: ConnectorDefinition): connector is DestinationDefinitionRead {
  return (connector as DestinationDefinitionRead).destinationDefinitionId !== undefined;
}

export function isDestinationDefinitionSpecification(
  connector: ConnectorDefinitionSpecification
): connector is DestinationDefinitionSpecificationRead {
  return (connector as DestinationDefinitionSpecificationRead).destinationDefinitionId !== undefined;
}
