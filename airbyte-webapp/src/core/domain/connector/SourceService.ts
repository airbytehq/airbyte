import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { CommonRequestError } from "core/request/CommonRequestError";
import { LogsRequestError } from "core/request/LogsRequestError";
import Status from "core/statuses";

import { ConnectionConfiguration } from "../connection";
import { Scheduler, Schema, Source } from "./types";

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
    return this.fetch<Source>(`${this.url}/update`, body);
  }

  public delete(sourceId: string): Promise<Source> {
    return this.fetch<Source>(`${this.url}/delete`, { sourceId });
  }

  public async discoverSchema(sourceId: string): Promise<Schema> {
    // needs proper type and refactor of CommonRequestError
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result = await this.fetch<any>(`${this.url}/discover_schema`, {
      sourceId,
    });

    if (result.jobInfo?.status === Status.FAILED || !result.catalog) {
      // @ts-ignore address this case
      const e = new CommonRequestError(result);
      // Generate error with failed status and received logs
      e._status = 400;
      // @ts-ignore address this case
      e.response = result.jobInfo;
      throw e;
    }

    return {
      catalog: result.catalog,
      jobInfo: result.jobInfo,
      catalogId: result.catalogId,
      id: sourceId,
    };
  }
}

export { SourceService };
