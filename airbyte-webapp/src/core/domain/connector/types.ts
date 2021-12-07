import { ConnectionSpecification } from "core/domain/connection";
import { DestinationSyncMode } from "core/domain/catalog";
import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

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
