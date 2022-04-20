import { getSourceDefinitionSpecification } from "../../request/GeneratedApi";

class SourceDefinitionSpecificationService {
  public get(sourceDefinitionId: string) {
    return getSourceDefinitionSpecification({ sourceDefinitionId });
  }
}

export { SourceDefinitionSpecificationService };
