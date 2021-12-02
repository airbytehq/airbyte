import { ConnectorDefinitionSpecification } from "core/domain/connector";

export function makeConnectionConfigurationPath(path: string[]): string {
  return `connectionConfiguration.${path.join(".")}`;
}

export function serverProvidedOauthPaths(
  connector?: ConnectorDefinitionSpecification
): { [key: string]: { path_in_connector_config: string[] } } {
  return {
    ...(connector?.advancedAuth?.oauthConfigSpecification
      .completeOAuthOutputSpecification?.properties ?? {}),
    ...(connector?.advancedAuth?.oauthConfigSpecification
      .completeOAuthServerOutputSpecification?.properties ?? {}),
  };
}
