import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { Connection } from "./types";
import { CommonRequestError } from "../../request/CommonRequestError";

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

  public async delete(connectionId: string): Promise<Connection> {
    const result = await this.fetch<any>(`${this.url}/delete`, {
      connectionId,
    });

    if (result.status === "failure") {
      throw new CommonRequestError(result, result.message);
    }

    return result;
  }
}

export { ConnectionService };
