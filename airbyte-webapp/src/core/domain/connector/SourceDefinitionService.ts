import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { SourceDefinition } from "core/resources/SourceDefinition";

class SourceDefinitionService extends AirbyteRequestService {
  get url() {
    return "source_definitions";
  }

  public update(body: SourceDefinition): Promise<any> {
    return this.fetch(`${this.url}/update`, body);
  }
}

export const sourceDefinitionService = new SourceDefinitionService();
