import { AirbyteRequestService } from "core/request/AirbyteRequestService";

class SourceService extends AirbyteRequestService {
  get url(): string {
    return "sources";
  }
}

export { SourceService };
