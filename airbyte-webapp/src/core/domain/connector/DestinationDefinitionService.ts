import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import {
  createCustomDestinationDefinition,
  CustomDestinationDefinitionCreate,
  CustomDestinationDefinitionUpdate,
  DestinationDefinitionIdWithWorkspaceId,
  getDestinationDefinitionForWorkspace,
  listDestinationDefinitionsForWorkspace,
  listLatestDestinationDefinitions,
  updateCustomDestinationDefinition,
} from "../../request/AirbyteClient";

export class DestinationDefinitionService extends AirbyteRequestService {
  public get(body: DestinationDefinitionIdWithWorkspaceId) {
    return getDestinationDefinitionForWorkspace(body, this.requestOptions);
  }

  public list(workspaceId: string) {
    return listDestinationDefinitionsForWorkspace({ workspaceId }, this.requestOptions);
  }

  public listLatest() {
    return listLatestDestinationDefinitions(this.requestOptions);
  }

  public update(body: CustomDestinationDefinitionUpdate) {
    return updateCustomDestinationDefinition(body, this.requestOptions);
  }

  public create(body: CustomDestinationDefinitionCreate) {
    return createCustomDestinationDefinition(body, this.requestOptions);
  }
}
