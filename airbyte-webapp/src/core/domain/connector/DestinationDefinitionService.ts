import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

class DestinationDefinitionService extends AirbyteRequestService {
  get url() {
    return "destination_definitions";
  }

  public update(body: DestinationDefinition): Promise<DestinationDefinition> {
    return this.fetch(`${this.url}/update`, body) as any;
  }
}

export { DestinationDefinitionService };
