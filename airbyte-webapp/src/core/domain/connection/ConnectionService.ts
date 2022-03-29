import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { Connection } from "./types";

class ConnectionService extends AirbyteRequestService {
  get url() {
    return "connections";
  }

  public async sync(connectionId: string): Promise<unknown> {
    const rs = await this.fetch<Connection>(`${this.url}/sync`, {
      connectionId,
    });

    return rs;
  }

  public async reset(connectionId: string): Promise<unknown> {
    const rs = await this.fetch<Connection>(`${this.url}/reset`, {
      connectionId,
    });

    return rs;
  }
}

export { ConnectionService };
