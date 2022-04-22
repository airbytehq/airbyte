import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { getDestinationDefinitionSpecification } from "../../request/GeneratedApi";

export class DestinationDefinitionSpecificationService extends AirbyteRequestService {
  public get(destinationDefinitionId: string, workspaceId: string) {
    return getDestinationDefinitionSpecification({ destinationDefinitionId, workspaceId }, this.requestOptions);
  }
}
