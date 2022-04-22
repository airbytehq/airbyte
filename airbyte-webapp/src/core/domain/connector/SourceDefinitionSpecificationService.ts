import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import { getSourceDefinitionSpecification } from "../../request/GeneratedApi";

export class SourceDefinitionSpecificationService extends AirbyteRequestService {
  public get(sourceDefinitionId: string, workspaceId: string) {
    return getSourceDefinitionSpecification({ sourceDefinitionId, workspaceId }, this.requestOptions);
  }
}
