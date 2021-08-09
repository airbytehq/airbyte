import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { Workspace } from "./types";

class WorkspaceService extends AirbyteRequestService {
  get url() {
    return `workspaces`;
  }

  public async create(workspaceCreatPayload: {
    name: string;
  }): Promise<Workspace> {
    const workspace = await this.fetch<Workspace>(
      `${this.url}/create`,
      workspaceCreatPayload
    );

    return workspace;
  }
}

export { WorkspaceService };
