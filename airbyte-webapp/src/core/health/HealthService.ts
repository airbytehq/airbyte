import { AirbyteRequestService } from "../request/AirbyteRequestService";
import { getHealthCheck } from "../request/GeneratedApi";

export class HealthService extends AirbyteRequestService {
  health() {
    return getHealthCheck(this.requestOptions);
  }
}
