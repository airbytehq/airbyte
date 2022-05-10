import {
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  ConnectorT,
  Source,
  SourceDefinition,
  SourceDefinitionSpecification,
} from "./types";

export function isSource(connector: ConnectorT): connector is Source {
  return "sourceId" in connector;
}

export function isSourceDefinition(connector: ConnectorDefinition): connector is SourceDefinition {
  return (connector as SourceDefinition).sourceDefinitionId !== undefined;
}

export function isSourceDefinitionSpecification(
  connector: ConnectorDefinitionSpecification
): connector is SourceDefinitionSpecification {
  return (connector as SourceDefinitionSpecification).sourceDefinitionId !== undefined;
}

// eslint-disable-next-line no-template-curly-in-string
export const SOURCE_NAMESPACE_TAG = "${SOURCE_NAMESPACE}";
