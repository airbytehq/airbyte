import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { FormBlock } from "core/form/types";
import { naturalComparator } from "utils/objects";

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

export function OrderComparator(a: FormBlock, b: FormBlock): number {
  const aIsNumber = Number.isInteger(a.order);
  const bIsNumber = Number.isInteger(b.order);

  switch (true) {
    case aIsNumber && bIsNumber:
      return (a.order as number) - (b.order as number);
    case aIsNumber && !bIsNumber:
      return -1;
    case bIsNumber && !aIsNumber:
      return 1;
    default:
      return naturalComparator(a.fieldKey, b.fieldKey);
  }
}
