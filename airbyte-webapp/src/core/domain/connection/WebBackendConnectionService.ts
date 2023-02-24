import {
  WebBackendConnectionCreate,
  WebBackendConnectionUpdate,
  webBackendCreateConnection,
  webBackendGetConnection,
  webBackendListConnectionsForWorkspace,
  webBackendUpdateConnection,
} from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  FilterConnectionRequestBody,
  webBackendListFilteredConnectionsForWorkspace,
  getConnectionFilterParams,
} from "../../request/DaspireClient";

export class WebBackendConnectionService extends AirbyteRequestService {
  public getConnection(connectionId: string, withRefreshedCatalog?: boolean) {
    return webBackendGetConnection({ connectionId, withRefreshedCatalog }, this.requestOptions);
  }

  public list(workspaceId: string) {
    return webBackendListConnectionsForWorkspace({ workspaceId }, this.requestOptions);
  }

  public filteredList(filters: FilterConnectionRequestBody) {
    return webBackendListFilteredConnectionsForWorkspace(filters, this.requestOptions);
  }

  public update(payload: WebBackendConnectionUpdate) {
    return webBackendUpdateConnection(payload, this.requestOptions);
  }

  public create(payload: WebBackendConnectionCreate) {
    return webBackendCreateConnection(payload, this.requestOptions);
  }

  public filtersLists() {
    return getConnectionFilterParams(this.requestOptions);
  }
}
