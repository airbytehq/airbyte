import {
  WebBackendConnectionCreate,
  WebBackendConnectionListRequestBody,
  WebBackendConnectionUpdate,
  webBackendCreateConnection,
  webBackendGetConnection,
  webBackendListConnectionsForWorkspace,
  webBackendUpdateConnection,
} from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class WebBackendConnectionService extends AirbyteRequestService {
  public getConnection(connectionId: string, withRefreshedCatalog?: boolean) {
    return webBackendGetConnection({ connectionId, withRefreshedCatalog }, this.requestOptions);
  }

  public list(payload: WebBackendConnectionListRequestBody) {
    return webBackendListConnectionsForWorkspace(payload, this.requestOptions);
  }

  public update(payload: WebBackendConnectionUpdate) {
    return webBackendUpdateConnection(payload, this.requestOptions);
  }

  public create(payload: WebBackendConnectionCreate) {
    return webBackendCreateConnection(payload, this.requestOptions);
  }
}
