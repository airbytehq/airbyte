import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";
import { isSourceDefinition } from "./source";

export type ConnectorDefinition = SourceDefinition | DestinationDefinition;

export function isConnectorDeprecated(connector: ConnectorDefinition): boolean {
  return !connector.latestDockerImageTag;
}

export class Connector {
  static id(connector: ConnectorDefinition): string {
    return isSourceDefinition(connector)
      ? connector.sourceDefinitionId
      : connector.destinationDefinitionId;
  }

  static isDeprecated(connector: ConnectorDefinition): boolean {
    return !connector.latestDockerImageTag;
  }

  static hasNewerVersion(connector: ConnectorDefinition): boolean {
    return (
      !Connector.isDeprecated(connector) &&
      connector.latestDockerImageTag !== connector.dockerImageTag
    );
  }
}
