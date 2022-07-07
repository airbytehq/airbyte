import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import {
  createDestinationDefinition,
  DestinationDefinitionCreate,
  DestinationDefinitionUpdate,
  getDestinationDefinition,
  listDestinationDefinitions,
  listLatestDestinationDefinitions,
  updateDestinationDefinition,
} from "../../request/AirbyteClient";

export class DestinationDefinitionService extends AirbyteRequestService {
  public get(destinationDefinitionId: string) {
    return getDestinationDefinition({ destinationDefinitionId }, this.requestOptions);
  }

  public list() {
    return listDestinationDefinitions(this.requestOptions);
  }

  public listLatest() {
    return listLatestDestinationDefinitions(this.requestOptions);
  }

  public update(body: DestinationDefinitionUpdate) {
    return updateDestinationDefinition(body, this.requestOptions);
  }

  public create(body: DestinationDefinitionCreate) {
    return createDestinationDefinition(body, this.requestOptions);
  }
}
