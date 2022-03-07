import { ReadShape, Resource, SchemaDetail } from "rest-hooks";

import BaseResource from "./BaseResource";
import Status from "core/statuses";
import { ConnectionSpecification } from "core/domain/connection";
import { JobInfo } from "core/domain/job/Job";
import { LogsRequestError } from "core/request/LogsRequestError";

export interface Scheduler {
  status: string;
  message: string;
  jobInfo?: JobInfo;
}

export default class SchedulerResource
  extends BaseResource
  implements Scheduler {
  readonly status: string = "";
  readonly message: string = "";
  readonly jobInfo: JobInfo | undefined = undefined;

  pk(): string {
    return Date.now().toString();
  }

  static urlRoot = "scheduler";

  static sourceCheckConnectionShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Scheduler>> {
    return {
      ...super.detailShape(),
      getFetchKey: (params: {
        sourceDefinitionId: string;
        connectionConfiguration: ConnectionSpecification;
      }) => `POST /sources/check_connection` + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, unknown>>
      ): Promise<Scheduler> => {
        const url = !params.sourceId
          ? `${this.url(params)}/sources/check_connection`
          : params.connectionConfiguration
          ? `${super.rootUrl()}sources/check_connection_for_update`
          : `${super.rootUrl()}sources/check_connection`;

        const result = await this.fetch("post", url, params);

        // If check connection for source has status 'failed'
        if (result.status === Status.FAILED) {
          const jobInfo = {
            ...result.jobInfo,
            status: result.status,
          };

          throw new LogsRequestError(jobInfo, jobInfo, result.message);
        }

        return result;
      },
      schema: this,
    };
  }

  static destinationCheckConnectionShape<T extends typeof Resource>(
    this: T
  ): ReadShape<SchemaDetail<Scheduler>> {
    return {
      ...super.detailShape(),
      getFetchKey: (params: {
        destinationDefinitionId: string;
        connectionConfiguration: ConnectionSpecification;
      }) => `POST /destinations/check_connection` + JSON.stringify(params),
      fetch: async (
        params: Readonly<Record<string, unknown>>
      ): Promise<Scheduler> => {
        const url = !params.destinationId
          ? `${this.url(params)}/destinations/check_connection`
          : params.connectionConfiguration
          ? `${super.rootUrl()}destinations/check_connection_for_update`
          : `${super.rootUrl()}destinations/check_connection`;

        const result = await this.fetch("post", url, params);

        // If check connection for destination has status 'failed'
        if (result.status === Status.FAILED) {
          const jobInfo = {
            ...result.jobInfo,
            status: result.status,
          };

          throw new LogsRequestError(jobInfo, jobInfo, result.message);
        }

        return result;
      },
      schema: this,
    };
  }
}
