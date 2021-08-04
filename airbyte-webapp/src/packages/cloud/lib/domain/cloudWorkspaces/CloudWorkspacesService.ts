import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { CloudWorkspace } from "./types";

class CloudWorkspacesService extends AirbyteRequestService {
  get url() {
    return `cloud_workspaces`;
  }

  public async list(): Promise<CloudWorkspace[]> {
    const rs = ((await this.fetch(
      `${this.url}/list`,
      {}
    )) as any) as CloudWorkspace[];

    return rs;
  }

  public async get(workspaceId: string): Promise<CloudWorkspace> {
    const rs = ((await this.fetch(`${this.url}/get`, {
      workspaceId,
    })) as any) as CloudWorkspace;

    return rs;
  }

  public async create(cloudWorkspace: {
    name: string;
  }): Promise<CloudWorkspace> {
    const rs = ((await this.fetch(
      `${this.url}/create`,
      cloudWorkspace
    )) as any) as CloudWorkspace;

    return rs;
  }
}

export { CloudWorkspacesService };
