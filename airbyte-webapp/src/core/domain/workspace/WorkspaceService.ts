import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { Workspace, WorkspaceState } from "./Workspace";

class WorkspaceService extends AirbyteRequestService {
  get url() {
    return "workspaces";
  }

  public async get(workspaceId: string): Promise<Workspace> {
    return await this.fetch<Workspace>(`${this.url}/get`, {
      workspaceId,
    });
  }

  public async list(): Promise<{ workspaces: Workspace[] }> {
    return await this.fetch<{ workspaces: Workspace[] }>(`${this.url}/list`);
  }

  public async update(payload: Record<string, unknown>): Promise<Workspace> {
    return await this.fetch<Workspace>(`${this.url}/update`, payload);
  }

  public async getState(workspaceId: string): Promise<WorkspaceState> {
    return await this.fetch<WorkspaceState>(`web_backend/workspace/state`, {
      workspaceId,
    });
  }
}

export { WorkspaceService };
