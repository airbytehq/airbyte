import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { DestinationDefinitionSpecification } from "./types";

class DestinationDefinitionSpecificationService extends AirbyteRequestService {
  get url(): string {
    return "destination_definition_specifications";
  }

  public get(destinationDefinitionId: string, workspaceId: string): Promise<DestinationDefinitionSpecification> {
    return this.fetch<DestinationDefinitionSpecification>(`${this.url}/get`, {
      destinationDefinitionId,
      workspaceId,
    });
  }
}

export { DestinationDefinitionSpecificationService };
