import { getSourceDefinitionSpecification } from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class SourceDefinitionSpecificationService extends AirbyteRequestService {
  public get(sourceDefinitionId: string, workspaceId: string) {
    return getSourceDefinitionSpecification({ sourceDefinitionId, workspaceId }, this.requestOptions);
  }
}
