import {
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  ConnectorT,
  SourceDefinitionSpecificationDraft,
} from "./types";
import {
  DestinationDefinitionSpecificationRead,
  SourceDefinitionRead,
  SourceDefinitionSpecificationRead,
  SourceRead,
} from "../../request/AirbyteClient";

export function isSource(connector: ConnectorT): connector is SourceRead {
  return "sourceId" in connector;
}

export function isSourceDefinition(connector: ConnectorDefinition): connector is SourceDefinitionRead {
  return (connector as SourceDefinitionRead).sourceDefinitionId !== undefined;
}

export function isSourceDefinitionSpecification(
  connector: ConnectorDefinitionSpecification
): connector is SourceDefinitionSpecificationRead {
  return (connector as SourceDefinitionSpecificationRead).sourceDefinitionId !== undefined;
}

export function isSourceDefinitionSpecificationDraft(
  connector: ConnectorDefinitionSpecification | SourceDefinitionSpecificationDraft
): connector is SourceDefinitionSpecificationDraft {
  return (
    (connector as SourceDefinitionSpecificationRead).sourceDefinitionId === undefined &&
    (connector as DestinationDefinitionSpecificationRead).destinationDefinitionId === undefined
  );
}

// eslint-disable-next-line no-template-curly-in-string
export const SOURCE_NAMESPACE_TAG = "${SOURCE_NAMESPACE}";
