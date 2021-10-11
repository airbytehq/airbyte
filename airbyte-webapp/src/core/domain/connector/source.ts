import { SourceDefinition } from "core/resources/SourceDefinition";
import {
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  SourceDefinitionSpecification,
} from "./types";

export function isSourceDefinition(
  connector: ConnectorDefinition
): connector is SourceDefinition {
  return (connector as SourceDefinition).sourceDefinitionId !== undefined;
}

export function isSourceDefinitionSpecification(
  connector: ConnectorDefinitionSpecification
): connector is SourceDefinitionSpecification {
  return (
    (connector as SourceDefinitionSpecification).sourceDefinitionId !==
    undefined
  );
}

// eslint-disable-next-line no-template-curly-in-string
export const SOURCE_NAMESPACE_TAG = "${SOURCE_NAMESPACE}";
