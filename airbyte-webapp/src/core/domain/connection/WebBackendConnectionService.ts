import {
  WebBackendConnectionCreate,
  WebBackendConnectionUpdate,
  webBackendCreateConnection,
  webBackendGetConnection,
  webBackendListConnectionsForWorkspace,
  webBackendUpdateConnection,
  getConnectionFilterParams,
} from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  FilterConnectionRequestBody,
  webBackendListFilteredConnectionsForWorkspace,
  ConnectionData,
  webBackendListFilteredConnectionsStatus,
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
  public getConnectionsStatus(payload: ConnectionData) {
    return webBackendListFilteredConnectionsStatus(payload, this.requestOptions);
  }
  public update(payload: WebBackendConnectionUpdate, connectionId: string) {
    return webBackendUpdateConnection(payload, connectionId, this.requestOptions);
  }

  public create(payload: WebBackendConnectionCreate) {
    return webBackendCreateConnection(payload, this.requestOptions);
  }

  public filtersLists(workspaceId: string) {
    // workspaceId: string
    return getConnectionFilterParams({ workspaceId }, this.requestOptions);
  }
}
