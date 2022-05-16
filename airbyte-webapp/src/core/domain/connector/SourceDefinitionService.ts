import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { SourceDefinition } from "./types";

class SourceDefinitionService extends AirbyteRequestService {
  get url(): string {
    return "source_definitions";
  }

  public get(sourceDefinitionId: string): Promise<SourceDefinition> {
    return this.fetch<SourceDefinition>(`${this.url}/get`, {
      sourceDefinitionId,
    });
  }

  public list(workspaceId: string): Promise<{ sourceDefinitions: SourceDefinition[] }> {
    return this.fetch(`${this.url}/list`, {
      workspaceId,
    });
  }

  public listLatest(workspaceId: string): Promise<{ sourceDefinitions: SourceDefinition[] }> {
    return this.fetch(`${this.url}/list_latest`, {
      workspaceId,
    });
  }

  public update(body: { sourceDefinitionId: string; dockerImageTag: string }): Promise<SourceDefinition> {
    return this.fetch<SourceDefinition>(`${this.url}/update`, body);
  }

  public create(body: CreateSourceDefinitionPayload): Promise<SourceDefinition> {
    return this.fetch<SourceDefinition>(`${this.url}/create`, body);
  }
}

export type CreateSourceDefinitionPayload = {
  name: string;
  documentationUrl: string;
  dockerImageTag: string;
  dockerRepository: string;
};

export { SourceDefinitionService };
