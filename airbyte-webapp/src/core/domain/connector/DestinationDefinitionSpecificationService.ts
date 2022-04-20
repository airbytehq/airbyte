import { getDestinationDefinitionSpecification } from "../../request/GeneratedApi";

export class DestinationDefinitionSpecificationService {
  public get(destinationDefinitionId: string) {
    return getDestinationDefinitionSpecification({ destinationDefinitionId });
  }
}
