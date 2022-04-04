import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { Workspace } from "./Workspace";

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
}

export { WorkspaceService };
