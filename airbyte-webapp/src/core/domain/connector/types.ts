import {
  ConnectionConfiguration,
  ConnectionSpecification,
} from "core/domain/connection";
import { DestinationSyncMode } from "core/domain/catalog";

export enum ReleaseStage {
  "ALPHA" = "alpha",
  "BETA" = "beta",
  "GENERALLY_AVAILABLE" = "generally_available",
  "CUSTOM" = "custom",
}

export interface DestinationDefinition {
  destinationDefinitionId: string;
  name: string;
  dockerRepository: string;
  dockerImageTag: string;
  latestDockerImageTag: string;
  documentationUrl: string;
  icon: string;
  releaseStage?: ReleaseStage;
}

export interface SourceDefinition {
  sourceDefinitionId: string;
  name: string;
  dockerRepository: string;
  dockerImageTag: string;
  latestDockerImageTag: string;
  documentationUrl: string;
  icon: string;
  releaseStage?: ReleaseStage;
}

export type ConnectorDefinition = SourceDefinition | DestinationDefinition;

type AuthFlowTypes = "oauth2.0";

interface AuthSpecification {
  type: AuthFlowTypes;
  oauth2Specification: {
    rootObject?: string[];
    oauthFlowInitParameters?: string[][];
    oauthFlowOutputParameters?: string[][];
  };
}

type AdvancedAuthInput = {
  properties: {
    [key: string]: { path_in_connector_config: string[] };
  };
};

interface AdvancedAuth {
  authFlowType: AuthFlowTypes;
  predicateKey: string[];
  predicateValue: string;
  oauthConfigSpecification: {
    completeOAuthOutputSpecification?: AdvancedAuthInput;
    completeOAuthServerInputSpecification?: AdvancedAuthInput;
    completeOAuthServerOutputSpecification?: AdvancedAuthInput;
    oauthUserInputFromConnectorConfigSpecification?: AdvancedAuthInput;
  };
}

interface ConnectorDefinitionSpecificationBase {
  connectionSpecification: ConnectionSpecification;
  documentationUrl: string;
  authSpecification?: AuthSpecification;
  advancedAuth?: AdvancedAuth;
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
  oAuthInputConfiguration: Record<string, unknown>;
}

export interface DestinationGetConsentPayload {
  redirectUrl: string;
  destinationDefinitionId: string;
  workspaceId: string;
  oAuthInputConfiguration: Record<string, unknown>;
}

export interface Source {
  sourceId: string;
  name: string;
  sourceName: string;
  workspaceId: string;
  sourceDefinitionId: string;
  connectionConfiguration: ConnectionConfiguration;
}

export interface Destination {
  destinationId: string;
  name: string;
  destinationName: string;
  workspaceId: string;
  destinationDefinitionId: string;
  connectionConfiguration: ConnectionConfiguration;
}
