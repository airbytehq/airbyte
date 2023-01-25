import { WebBackendGeographiesListResult, webBackendListGeographies } from "core/request/AirbyteClient";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";

export class GeographiesService extends AirbyteRequestService {
  public async list(): Promise<WebBackendGeographiesListResult> {
    return webBackendListGeographies(this.requestOptions);
  }
}
