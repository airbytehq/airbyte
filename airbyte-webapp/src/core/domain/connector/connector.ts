import { isSourceDefinition, isSourceDefinitionSpecification } from "./source";
import { ConnectorDefinition, ConnectorDefinitionSpecification } from "./types";
import { Constants } from "constants/constants";

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
      (!Connector.isDeprecated(connector) &&
        connector.latestDockerImageTag !== connector.dockerImageTag) ||
      connector.dockerImageTag === Constants.DEV_IMAGE_TAG
    );
  }
}

export class ConnectorSpecification {
  static id(connector: ConnectorDefinitionSpecification): string {
    return isSourceDefinitionSpecification(connector)
      ? connector.sourceDefinitionId
      : connector.destinationDefinitionId;
  }
}
