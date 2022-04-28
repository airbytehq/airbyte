import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { CommonRequestError } from "core/request/CommonRequestError";

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

  public async delete(connectionId: string): Promise<void> {
    // needs proper type and refactor of CommonRequestError
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
