import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { CloudWorkspace } from "./types";

class CloudWorkspacesService extends AirbyteRequestService {
  get url() {
    return `cloud_workspaces`;
  }

  public async list(): Promise<CloudWorkspace[]> {
    const { workspaces } = await this.fetch<{ workspaces: CloudWorkspace[] }>(
      `${this.url}/list`,
      {}
    );

    return workspaces;
  }

  public async get(workspaceId: string): Promise<CloudWorkspace> {
    const cloudWorkspace = await this.fetch<CloudWorkspace>(`${this.url}/get`, {
      workspaceId,
    });

    return cloudWorkspace;
  }

  public async create(cloudWorkspaceCreatePayload: {
    name: string;
    billingUsedId: string;
    workspaceId: string;
  }): Promise<CloudWorkspace> {
    return await this.fetch<CloudWorkspace>(
      `${this.url}/create`,
      cloudWorkspaceCreatePayload
    );
  }
}

export { CloudWorkspacesService };
