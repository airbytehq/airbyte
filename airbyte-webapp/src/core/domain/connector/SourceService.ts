import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { ConnectionConfiguration } from "../connection";
import { Scheduler, Source } from "./types";
import Status from "core/statuses";
import { LogsRequestError } from "core/request/LogsRequestError";

class SourceService extends AirbyteRequestService {
  get url(): string {
    return "sources";
  }

  public async check_connection(
    params: {
      sourceId?: string;
      connectionConfiguration?: ConnectionConfiguration;
    },
    requestParams?: RequestInit
  ): Promise<Scheduler> {
    const url = !params.sourceId
      ? `scheduler/${this.url}/check_connection`
      : params.connectionConfiguration
      ? `${this.url}/check_connection_for_update`
      : `${this.url}/check_connection`;

    // migrated from rest-hooks. Needs proper fix to `Scheduler` type
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result = await this.fetch<any>(url, params, requestParams);

    // If check connection for source has status 'failed'
    if (result.status === Status.FAILED) {
      const jobInfo = {
        ...result.jobInfo,
        status: result.status,
      };

      throw new LogsRequestError(jobInfo, jobInfo, result.message);
    }

    return result;
  }

  public get(sourceId: string): Promise<Source> {
    return this.fetch<Source>(`${this.url}/get`, {
      sourceId,
    });
  }

  public list(workspaceId: string): Promise<{ sources: Source[] }> {
    return this.fetch(`${this.url}/list`, {
      workspaceId,
    });
  }

  public create(body: {
    name: string;
    sourceDefinitionId?: string;
    workspaceId: string;
    connectionConfiguration: ConnectionConfiguration;
  }): Promise<Source> {
    return this.fetch<Source>(`${this.url}/create`, body);
  }

  public update(body: {
    sourceId: string;
    name: string;
    connectionConfiguration: ConnectionConfiguration;
  }): Promise<Source> {
    return this.fetch<Source>(`${this.url}/create`, body);
  }

  public delete(sourceId: string): Promise<Source> {
    return this.fetch<Source>(`${this.url}/delete`, { sourceId });
  }
}

export { SourceService };
