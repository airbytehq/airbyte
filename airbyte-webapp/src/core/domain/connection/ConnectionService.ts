import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { Connection } from "./types";

class ConnectionService extends AirbyteRequestService {
  get url() {
    return "web_backend/connections";
  }

  public async getConnection(
    connectionId: string,
    withRefreshedCatalog?: boolean
  ): Promise<Connection> {
    const rs = ((await this.fetch(`${this.url}/get`, {
      connectionId,
      withRefreshedCatalog,
    })) as any) as Connection;

    return rs;
  }
}

export { ConnectionService };
