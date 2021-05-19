import { AirbyteRequestService } from "core/request/AirbyteRequestService";

class HealthService extends AirbyteRequestService {
  async health(): Promise<any> {
    const path = `${AirbyteRequestService.rootUrl}health`;
    await fetch(path, {
      method: "GET",
    });
  }
}

export { HealthService };
