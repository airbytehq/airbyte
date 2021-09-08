import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { SourceDefinition } from "core/resources/SourceDefinition";

class SourceDefinitionService extends AirbyteRequestService {
  get url() {
    return "source_definitions";
  }

  public update(body: SourceDefinition): Promise<SourceDefinition> {
    return this.fetch(`${this.url}/update`, body) as any;
  }
}

export { SourceDefinitionService };
