import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { RequestMiddleware } from "core/request/RequestMiddleware";

class HealthService extends AirbyteRequestService {
  constructor(
    requestSigner: RequestMiddleware[] = [],
    rootUrl: string = AirbyteRequestService.rootUrl
  ) {
    super(requestSigner, rootUrl);
  }

  async health(): Promise<void> {
    await this.fetch("health", undefined, {
      method: "GET",
    });
  }
}

export { HealthService };
