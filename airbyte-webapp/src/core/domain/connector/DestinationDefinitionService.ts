import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import {
  createDestinationDefinition,
  DestinationDefinitionCreate,
  DestinationDefinitionUpdate,
  getDestinationDefinition,
  listDestinationDefinitionsForWorkspace,
  updateDestinationDefinition,
} from "../../request/GeneratedApi";
import { DestinationDefinition } from "./types";

export class DestinationDefinitionService extends AirbyteRequestService {
  get url(): string {
    return "destination_definitions";
  }

  public get(destinationDefinitionId: string) {
    return getDestinationDefinition({ destinationDefinitionId });
  }

  public list(workspaceId: string) {
    return listDestinationDefinitionsForWorkspace({ workspaceId });
  }

  public listLatest(workspaceId: string): Promise<{ destinationDefinitions: DestinationDefinition[] }> {
    // TODO: List Latest doesn't take a workspace Id.
    return this.fetch(`${this.url}/list_latest`, {
      workspaceId,
    });
  }

  public update(body: DestinationDefinitionUpdate) {
    return updateDestinationDefinition(body);
  }

  public create(body: DestinationDefinitionCreate) {
    return createDestinationDefinition(body);
  }
}
