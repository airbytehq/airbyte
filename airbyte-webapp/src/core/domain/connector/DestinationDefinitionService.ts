import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { DestinationDefinition } from "./types";

class DestinationDefinitionService extends AirbyteRequestService {
  get url(): string {
    return "destination_definitions";
  }

  public get(destinationDefinitionId: string): Promise<DestinationDefinition> {
    return this.fetch<DestinationDefinition>(`${this.url}/get`, {
      destinationDefinitionId,
    });
  }

  public list(workspaceId: string): Promise<{ destinationDefinitions: DestinationDefinition[] }> {
    return this.fetch(`${this.url}/list`, {
      workspaceId,
    });
  }

  public listLatest(workspaceId: string): Promise<{ destinationDefinitions: DestinationDefinition[] }> {
    return this.fetch(`${this.url}/list_latest`, {
      workspaceId,
    });
  }

  public update(body: { destinationDefinitionId: string; dockerImageTag: string }): Promise<DestinationDefinition> {
    return this.fetch<DestinationDefinition>(`${this.url}/update`, body);
  }

  public create(body: CreateDestinationDefinitionPayload): Promise<DestinationDefinition> {
    return this.fetch<DestinationDefinition>(`${this.url}/create`, body);
  }
}

export type CreateDestinationDefinitionPayload = {
  name: string;
  documentationUrl: string;
  dockerImageTag: string;
  dockerRepository: string;
};

export { DestinationDefinitionService };
