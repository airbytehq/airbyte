import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import {
  createCustomDestinationDefinition,
  CustomDestinationDefinitionCreate,
  DestinationDefinitionIdWithWorkspaceId,
  DestinationDefinitionUpdate,
  getDestinationDefinitionForWorkspace,
  listDestinationDefinitionsForWorkspace,
  listLatestDestinationDefinitions,
  updateDestinationDefinition,
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

  public update(body: DestinationDefinitionUpdate) {
    return updateDestinationDefinition(body, this.requestOptions);
  }

  public createCustom(body: CustomDestinationDefinitionCreate) {
    return createCustomDestinationDefinition(body, this.requestOptions);
  }
}
