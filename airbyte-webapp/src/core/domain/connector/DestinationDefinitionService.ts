import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { DestinationDefinition } from "./types";

class DestinationDefinitionService extends AirbyteRequestService {
  get url(): string {
    return "destination_definitions";
  }

  public update(body: DestinationDefinition): Promise<DestinationDefinition> {
    return this.fetch<DestinationDefinition>(`${this.url}/update`, body);
  }
}

export { DestinationDefinitionService };
