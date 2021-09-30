import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { CloudWorkspace } from "./types";

class CloudWorkspacesService extends AirbyteRequestService {
  get url() {
    return `cloud_workspaces`;
  }

  public async list(): Promise<CloudWorkspace[]> {
    const { workspaces } = await this.fetch<{ workspaces: CloudWorkspace[] }>(
      `${this.url}/list`
    );

    return workspaces;
  }

  public async get(workspaceId: string): Promise<CloudWorkspace> {
    const cloudWorkspace = await this.fetch<CloudWorkspace>(`${this.url}/get`, {
      workspaceId,
    });

    return cloudWorkspace;
  }

  public async remove(workspaceId: string): Promise<void> {
    return this.fetch<void>(`${this.url}/delete`, {
      workspaceId,
    });
  }

  public async listByUser(userId: string): Promise<CloudWorkspace[]> {
    const { workspaces } = await this.fetch<{ workspaces: CloudWorkspace[] }>(
      `web_backend/permissions/list_workspaces_by_user`,
      { userId }
    );

    return workspaces;
  }

  public async create(cloudWorkspaceCreatePayload: {
    name: string;
    userId: string;
  }): Promise<CloudWorkspace> {
    return this.fetch<CloudWorkspace>(
      `web_backend/permissioned_cloud_workspace/create`,
      cloudWorkspaceCreatePayload
    );
  }

  public async update(
    workspaceId: string,
    cloudWorkspaceCreatePayload: {
      name: string;
    }
  ): Promise<CloudWorkspace> {
    return this.fetch<CloudWorkspace>(
      `web_backend/permissioned_cloud_workspace/create`,
      { workspaceId, ...cloudWorkspaceCreatePayload }
    );
  }
}

export { CloudWorkspacesService };
