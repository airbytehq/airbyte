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

  public list(workspaceId: string): Promise<SourceDefinition[]> {
    return this.fetch<SourceDefinition[]>(`${this.url}/list`, {
      workspaceId,
    });
  }

  public listLatest(workspaceId: string): Promise<SourceDefinition[]> {
    return this.fetch<SourceDefinition[]>(`${this.url}/list_latest`, {
      workspaceId,
    });
  }

  public update(body: SourceDefinition): Promise<SourceDefinition> {
    return this.fetch<SourceDefinition>(`${this.url}/update`, body);
  }
}

export { SourceDefinitionService };
