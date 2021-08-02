import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { RequestMiddleware } from "core/request/RequestMiddleware";

import { CloudWorkspace } from "./types";

class CloudWorkspacesService extends AirbyteRequestService {
  constructor(requestSigner: RequestMiddleware, rootUrl: string) {
    super([requestSigner], rootUrl);
  }

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
}

export { CloudWorkspacesService };
