import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import {
  getSourceDefinitionForWorkspace,
  listLatestSourceDefinitions,
  listSourceDefinitionsForWorkspace,
  SourceDefinitionIdWithWorkspaceId,
  updateSourceDefinition,
  SourceDefinitionUpdate,
  CustomSourceDefinitionCreate,
  createCustomSourceDefinition,
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

  public update(body: SourceDefinitionUpdate) {
    return updateSourceDefinition(body, this.requestOptions);
  }

  public createCustom(body: CustomSourceDefinitionCreate) {
    return createCustomSourceDefinition(body, this.requestOptions);
  }
}
