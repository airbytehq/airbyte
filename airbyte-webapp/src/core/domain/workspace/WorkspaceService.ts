import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  getWorkspace,
  listWorkspaces,
  updateWorkspace,
  webBackendGetWorkspaceState,
  WebBackendWorkspaceState,
  WorkspaceIdRequestBody,
  WorkspaceUpdate,
} from "../../request/GeneratedApi";

export class WorkspaceService extends AirbyteRequestService {
  public get(body: WorkspaceIdRequestBody) {
    return getWorkspace(body, this.requestOptions);
  }

  public list() {
    return listWorkspaces(this.requestOptions);
  }

  public update(body: WorkspaceUpdate) {
    return updateWorkspace(body, this.requestOptions);
  }

  public getState(body: WebBackendWorkspaceState) {
    return webBackendGetWorkspaceState(body, this.requestOptions);
  }
}
