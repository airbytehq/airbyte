import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import {
  createCustomSourceDefinition,
  CustomSourceDefinitionCreate,
  getSourceDefinitionForWorkspace,
  listLatestSourceDefinitions,
  listSourceDefinitionsForWorkspace,
  CustomSourceDefinitionUpdate,
  updateCustomSourceDefinition,
  SourceDefinitionIdWithWorkspaceId,
} from "../../request/AirbyteClient";

export class SourceDefinitionService extends AirbyteRequestService {
  public get(body: SourceDefinitionIdWithWorkspaceId) {
    return getSourceDefinitionForWorkspace(body, this.requestOptions);
  }

  public list(workspaceId: string) {
    return listSourceDefinitionsForWorkspace({ workspaceId }, this.requestOptions);
  }

  public listLatest() {
    return listLatestSourceDefinitions(this.requestOptions);
  }

  public update(body: CustomSourceDefinitionUpdate) {
    return updateCustomSourceDefinition(body, this.requestOptions);
  }

  public create(body: CustomSourceDefinitionCreate) {
    return createCustomSourceDefinition(body, this.requestOptions);
  }
}
