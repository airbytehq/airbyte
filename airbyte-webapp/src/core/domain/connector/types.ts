import { ConnectionSpecification } from "core/domain/connection";
import { DestinationSyncMode } from "core/domain/catalog";
import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

export type ConnectorDefinition = SourceDefinition | DestinationDefinition;

interface ConnectorDefinitionSpecificationBase {
  connectionSpecification: ConnectionSpecification;
  documentationUrl: string;
  authSpecification?: {
    type: "oauth2.0";
    oauth2Specification: {
      rootObject?: string[];
      oauthFlowInitParameters?: string[][];
      oauthFlowOutputParameters?: string[][];
    };
  };
}

export type ConnectorDefinitionSpecification =
  | DestinationDefinitionSpecification
  | SourceDefinitionSpecification;

export interface DestinationDefinitionSpecification
  extends ConnectorDefinitionSpecificationBase {
  destinationDefinitionId: string;
  supportedDestinationSyncModes: DestinationSyncMode[];
  supportsDbt: boolean;
  supportsNormalization: boolean;
}

export interface SourceDefinitionSpecification
  extends ConnectorDefinitionSpecificationBase {
  sourceDefinitionId: string;
}

export interface SourceGetConsentPayload {
  redirectUrl: string;
  sourceDefinitionId: string;
  workspaceId: string;
}

export interface DestinationGetConsentPayload {
  redirectUrl: string;
  destinationDefinitionId: string;
  workspaceId: string;
}
