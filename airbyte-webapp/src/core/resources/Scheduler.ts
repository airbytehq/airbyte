import { Resource } from "rest-hooks";
import BaseResource, { NetworkError } from "./BaseResource";
import { propertiesType } from "./SourceDefinitionSpecification";
import { Attempt, JobItem } from "./Job";
import Status from "../statuses";

export type JobInfo = {
  job: JobItem;
  attempts: {
    attempt: Attempt;
    logs: { logLines: string[] };
  }[];
};

export interface Scheduler {
  status: string;
  message: string;
  jobInfo?: JobInfo;
}

export default class SchedulerResource extends BaseResource
  implements Scheduler {
  readonly status: string = "";
  readonly message: string = "";
  readonly jobInfo: JobInfo | undefined = undefined;

  pk() {
    return Date.now().toString();
  }

  static urlRoot = "scheduler";

  static sourceCheckConnectionShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: {
        sourceDefinitionId: string;
        connectionConfiguration: propertiesType;
      }) => `POST /sources/check_connection` + JSON.stringify(params),
      fetch: async (params: any): Promise<any> => {
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
            job: { ...result.jobInfo.job, status: result.status }
          };

          const e = new NetworkError(result);
          // Generate error with failed status and received logs
          e.status = 400;
          e.response = jobInfo;
          e.message = result.message || "";

          throw e;
        }

        return result;
      },
      schema: this
    };
  }

  static destinationCheckConnectionShape<T extends typeof Resource>(this: T) {
    return {
      ...super.detailShape(),
      getFetchKey: (params: {
        destinationDefinitionId: string;
        connectionConfiguration: propertiesType;
      }) => `POST /destinations/check_connection` + JSON.stringify(params),
      fetch: async (params: any): Promise<any> => {
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
            job: { ...result.jobInfo.job, status: result.status }
          };

          const e = new NetworkError(result);
          // Generate error with failed status and received logs
          e.status = 400;
          e.response = jobInfo;
          e.message = result.message || "";

          throw e;
        }

        return result;
      },
      schema: this
    };
  }
}
