import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { RequestMiddleware } from "core/request/RequestMiddleware";

class HealthService extends AirbyteRequestService {
  constructor(rootUrl: string, requestSigner: RequestMiddleware[] = []) {
    super(rootUrl, requestSigner);
  }

  async health(): Promise<void> {
    await this.fetch("health", undefined, {
      method: "GET",
    });
  }
}

export { HealthService };
