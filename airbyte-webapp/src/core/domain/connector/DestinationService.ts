import { ConnectionConfiguration } from "core/domain/connection";
import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { LogsRequestError } from "core/request/LogsRequestError";
import Status from "core/statuses";

import { Destination, Scheduler } from "./types";

class DestinationService extends AirbyteRequestService {
  get url(): string {
    return "destinations";
  }

  public async check_connection(
    params: {
      destinationId?: string;
      connectionConfiguration?: ConnectionConfiguration;
    },
    requestParams?: RequestInit
  ): Promise<Scheduler> {
    const url = !params.destinationId
      ? `scheduler/${this.url}/check_connection`
      : params.connectionConfiguration
      ? `${this.url}/check_connection_for_update`
      : `${this.url}/check_connection`;

    // migrated from rest-hooks. Needs proper fix to `Scheduler` type
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result = await this.fetch<any>(url, params, requestParams);

    // If check connection for destination has status 'failed'
    if (result.status === Status.FAILED) {
      const jobInfo = {
        ...result.jobInfo,
        status: result.status,
      };

      throw new LogsRequestError(jobInfo, jobInfo, result.message);
    }

    return result;
  }

  public get(destinationId: string): Promise<Destination> {
    return this.fetch<Destination>(`${this.url}/get`, {
      destinationId,
    });
  }

  public list(workspaceId: string): Promise<{ destinations: Destination[] }> {
    return this.fetch(`${this.url}/list`, {
      workspaceId,
    });
  }

  public create(body: {
    name: string;
    destinationDefinitionId?: string;
    workspaceId: string;
    connectionConfiguration: ConnectionConfiguration;
  }): Promise<Destination> {
    return this.fetch<Destination>(`${this.url}/create`, body);
  }

  public update(body: {
    destinationId: string;
    name: string;
    connectionConfiguration: ConnectionConfiguration;
  }): Promise<Destination> {
    return this.fetch<Destination>(`${this.url}/update`, body);
  }

  public delete(destinationId: string): Promise<Destination> {
    return this.fetch<Destination>(`${this.url}/delete`, { destinationId });
  }
}

export { DestinationService };
