import { AirbyteRequestService } from "core/request/AirbyteRequestService";

// import { toInnerModel } from "../catalog";

class SourceService extends AirbyteRequestService {
  get url() {
    return "sources";
  }
}

export const sourceService = new SourceService();
