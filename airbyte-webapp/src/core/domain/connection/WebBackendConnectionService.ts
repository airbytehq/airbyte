import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { Connection } from "./types";

class WebBackendConnectionService extends AirbyteRequestService {
  get url() {
    return "web_backend/connections";
  }

  public async getConnection(
    connectionId: string,
    withRefreshedCatalog?: boolean
  ): Promise<Connection> {
    return await this.fetch<Connection>(`${this.url}/get`, {
      connectionId,
      withRefreshedCatalog,
    });
  }

  public async list(workspaceId: string): Promise<Connection[]> {
    return await this.fetch<Connection[]>(`${this.url}/list`, {
      workspaceId,
    });
  }
}

export { WebBackendConnectionService };
