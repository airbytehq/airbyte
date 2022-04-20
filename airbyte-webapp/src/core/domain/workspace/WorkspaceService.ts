import { getWorkspace, listWorkspaces, updateWorkspace, webBackendGetWorkspaceState } from "../../request/GeneratedApi";

export class WorkspaceService {
  public get = getWorkspace;

  public list = listWorkspaces;

  public update = updateWorkspace;

  public getState = webBackendGetWorkspaceState;
}
