import {
  WebBackendConnectionCreate,
  WebBackendConnectionUpdate,
  webBackendCreateConnection,
  webBackendGetConnection,
  webBackendListConnectionsForWorkspace,
  webBackendUpdateConnection,
} from "../../request/GeneratedApi";

export class WebBackendConnectionService {
  public getConnection(connectionId: string, withRefreshedCatalog?: boolean) {
    return webBackendGetConnection({ connectionId, withRefreshedCatalog });
  }

  public list(workspaceId: string) {
    return webBackendListConnectionsForWorkspace({ workspaceId });
  }

  public update(payload: WebBackendConnectionUpdate) {
    return webBackendUpdateConnection(payload);
  }

  public create(payload: WebBackendConnectionCreate) {
    return webBackendCreateConnection(payload);
  }
}
