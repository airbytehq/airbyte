import { Resource } from "rest-hooks";
import BaseResource, { NetworkError } from "./BaseResource";
import { propertiesType } from "./SourceDefinitionSpecification";
import { Attempt, JobItem } from "./Job";

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
  job_info?: JobInfo;
}

export default class SchedulerResource extends BaseResource
  implements Scheduler {
  readonly status: string = "";
  readonly message: string = "";
  readonly job_info: JobInfo | undefined = undefined;

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
          : `${super.rootUrl()}sources/check_connection`;

        const result = await this.fetch("post", url, params);

        // If check connection for source has status 'failed'
        if (result.status === "failed") {
          // TODO: will delete jobInfo object if status comes right
          const jobInfo = {
            ...result.job_info,
            job: { ...result.job_info.job, status: result.status }
          };

          const e = new NetworkError(result);
          // Generate error with failed status and received logs
          e.status = 400;
          e.response = jobInfo;
          throw e;
        }

        return result;
      },
      schema: this.asSchema()
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
          : `${super.rootUrl()}destinations/check_connection`;

        const result = await this.fetch("post", url, params);

        // If check connection for destination has status 'failed'
        if (result.status === "failed") {
          const e = new NetworkError(result);
          // Generate error with failed status and received logs
          e.status = 400;
          e.response = result.job_info;
          throw e;
        }

        return result;
      },
      schema: this.asSchema()
    };
  }
}
