import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import {
  createSourceDefinition,
  getSourceDefinition,
  listLatestSourceDefinitions,
  listSourceDefinitions,
  SourceDefinitionCreate,
  SourceDefinitionUpdate,
  updateSourceDefinition,
} from "../../request/AirbyteClient";

export class SourceDefinitionService extends AirbyteRequestService {
  public get(sourceDefinitionId: string) {
    return getSourceDefinition({ sourceDefinitionId }, this.requestOptions);
  }

  public list() {
    return listSourceDefinitions(this.requestOptions);
  }

  public listLatest() {
    return listLatestSourceDefinitions(this.requestOptions);
  }

  public update(body: SourceDefinitionUpdate) {
    return updateSourceDefinition(body, this.requestOptions);
  }

  public create(body: SourceDefinitionCreate) {
    return createSourceDefinition(body, this.requestOptions);
  }
}
