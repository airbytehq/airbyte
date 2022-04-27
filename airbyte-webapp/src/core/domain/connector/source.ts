import { SourceDefinitionSpecificationRead } from "../../request/AirbyteClient";
import { ConnectorDefinition, ConnectorDefinitionSpecification, ConnectorT, Source, SourceDefinition } from "./types";

export function isSource(connector: ConnectorT): connector is Source {
  return "sourceId" in connector;
}

export function isSourceDefinition(connector: ConnectorDefinition): connector is SourceDefinition {
  return (connector as SourceDefinition).sourceDefinitionId !== undefined;
}

export function isSourceDefinitionSpecification(
  connector: ConnectorDefinitionSpecification
): connector is SourceDefinitionSpecificationRead {
  return (connector as SourceDefinitionSpecificationRead).sourceDefinitionId !== undefined;
}

// eslint-disable-next-line no-template-curly-in-string
export const SOURCE_NAMESPACE_TAG = "${SOURCE_NAMESPACE}";
