import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { CloudWorkspace } from "./types";

class WorkspaceService extends AirbyteRequestService {
  get url() {
    return `workspaces`;
  }

  public async create(workspaceCreatPayload: {
    name: string;
  }): Promise<CloudWorkspace> {
    const workspace = await this.fetch<CloudWorkspace>(
      `${this.url}/create`,
      workspaceCreatPayload
    );

    return workspace;
  }
}

export { WorkspaceService };
