import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { CommonRequestError } from "core/request/CommonRequestError";

import { Connection } from "./types";

class WebBackendConnectionService extends AirbyteRequestService {
  get url() {
    return "web_backend/connections";
  }

  public async getConnection(connectionId: string, withRefreshedCatalog?: boolean): Promise<Connection> {
    return await this.fetch<Connection>(`${this.url}/get`, {
      connectionId,
      withRefreshedCatalog,
    });
  }

  public async list(workspaceId: string): Promise<{ connections: Connection[] }> {
    return await this.fetch<{ connections: Connection[] }>(`${this.url}/list`, {
      workspaceId,
    });
  }

  public async update(payload: Record<string, unknown>): Promise<Connection> {
    // needs proper type and refactor of CommonRequestError
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result = await this.fetch<any>(`${this.url}/update`, payload);

    if (result.status === "failure") {
      throw new CommonRequestError(result, result.message);
    }

    return result;
  }

  public async create(payload: Record<string, unknown>): Promise<Connection> {
    // needs proper type and refactor of CommonRequestError
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result = await this.fetch<any>(`${this.url}/create`, payload);

    if (result.status === "failure") {
      throw new CommonRequestError(result, result.message);
    }

    return result;
  }
}

export { WebBackendConnectionService };
