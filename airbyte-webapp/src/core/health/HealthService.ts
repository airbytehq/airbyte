import { getHealthCheck } from "../request/AirbyteClient";
import { AirbyteRequestService } from "../request/AirbyteRequestService";

export class HealthService extends AirbyteRequestService {
  health() {
    return getHealthCheck(this.requestOptions);
  }
}
