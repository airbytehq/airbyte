import { ConnectionSpecification } from "core/domain/connection";
import { DestinationSyncMode } from "core/domain/catalog";

export interface ConnectorDefinitionSpecification {
  connectionSpecification: ConnectionSpecification;
  documentationUrl: string;
  auth?: {
    type: "oauth2.0";
    oauth_flow_init_parameters: [];
  };
}

export interface DestinationDefinitionSpecification
  extends ConnectorDefinitionSpecification {
  destinationDefinitionId: string;
  supportedDestinationSyncModes: DestinationSyncMode[];
  supportsDbt: boolean;
  supportsNormalization: boolean;
}

export interface SourceDefinitionSpecification
  extends ConnectorDefinitionSpecification {
  sourceDefinitionId: string;
}
