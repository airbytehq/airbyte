import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { SourceDefinition } from "./types";

class SourceDefinitionService extends AirbyteRequestService {
  get url(): string {
    return "source_definitions";
  }

  public update(body: SourceDefinition): Promise<SourceDefinition> {
    return this.fetch<SourceDefinition>(`${this.url}/update`, body);
  }
}

export { SourceDefinitionService };
