import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { SourceDefinitionSpecification } from "./types";

class SourceDefinitionSpecificationService extends AirbyteRequestService {
  get url(): string {
    return "source_definition_specifications";
  }

  public get(sourceDefinitionId: string, workspaceId: string): Promise<SourceDefinitionSpecification> {
    return this.fetch<SourceDefinitionSpecification>(`${this.url}/get`, {
      sourceDefinitionId,
      workspaceId,
    });
  }
}

export { SourceDefinitionSpecificationService };
