import { AirbyteRequestService } from "core/request/AirbyteRequestService";

class SourceService extends AirbyteRequestService {
  get url() {
    return "sources";
  }
}

export { SourceService };
