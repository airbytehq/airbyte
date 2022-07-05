import { getDestinationDefinitionSpecification } from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class DestinationDefinitionSpecificationService extends AirbyteRequestService {
  public get(destinationDefinitionId: string, workspaceId: string) {
    return getDestinationDefinitionSpecification({ destinationDefinitionId, workspaceId }, this.requestOptions);
  }
}
